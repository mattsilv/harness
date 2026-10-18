#!/usr/bin/env node
// Read-only delivery checks for a disposable evaluation repository.
// Usage: node eval/delivery.mjs <repo> <baseline-commit-sha>

import { execFileSync } from "node:child_process";
import { existsSync, lstatSync, realpathSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const safeGit = (cwd, ...args) => execFileSync("git", [
  "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null",
  "-c", "core.excludesFile=/dev/null", "-C", cwd, ...args,
], { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();

const failed = (reason) => ({
  committed: `fail: ${reason}`,
  on_branch: `fail: ${reason}`,
  default_untouched: `fail: ${reason}`,
});
const unverified = () => ({
  committed: "unverified",
  on_branch: "unverified",
  default_untouched: "unverified",
});
const repoFailure = (reason, pinned) => pinned === undefined || pinned === null ? unverified() : failed(reason);

function isAncestor(cwd, ancestor, ref) {
  try {
    safeGit(cwd, "merge-base", "--is-ancestor", ancestor, ref);
    return true;
  } catch {
    return false;
  }
}

/** Check that evaluation work is committed on a non-default branch, with the
 * pinned default-branch baseline unchanged. With no baseline, retain the
 * evaluator's historical single-root behavior for create/update runs. */
export function delivery(cwd, pinnedBaseline) {
  try {
    const root = resolve(cwd);
    if (!existsSync(root) || lstatSync(root).isSymbolicLink()) return repoFailure("repo path is missing or uses a symlink", pinnedBaseline);
    if (!existsSync(join(root, ".git")) || !lstatSync(join(root, ".git")).isDirectory()) {
      return repoFailure("repository metadata is missing or uses a symlink", pinnedBaseline);
    }
    if (realpathSync(safeGit(root, "rev-parse", "--show-toplevel")) !== realpathSync(root) || !safeGit(root, "rev-parse", "HEAD")) {
      return repoFailure("path is not the git repository root", pinnedBaseline);
    }

    let baseline = pinnedBaseline;
    if (baseline !== undefined && baseline !== null) {
      if (typeof baseline !== "string" || !/^(?:[a-f0-9]{40}|[a-f0-9]{64})$/.test(baseline)) {
        return failed("baseline must be a full commit SHA");
      }
      let actual;
      try { actual = safeGit(root, "rev-parse", "--verify", `${baseline}^{commit}`); } catch {}
      if (actual !== baseline) return failed("baseline commit does not exist in this repository");
    } else {
      baseline = safeGit(root, "rev-list", "--max-parents=0", "HEAD").split("\n").pop();
    }

    const defaultBranch = ["main", "master"].find((branch) => {
      try { safeGit(root, "rev-parse", "--verify", "-q", `refs/heads/${branch}`); return true; } catch { return false; }
    });
    if (!defaultBranch) return failed("no main or master branch");

    const head = safeGit(root, "rev-parse", "HEAD");
    if (!isAncestor(root, baseline, head)) return failed("baseline is not an ancestor of HEAD");
    const defaultRef = `refs/heads/${defaultBranch}`;
    const defaultTip = safeGit(root, "rev-parse", defaultRef);
    const branches = safeGit(root, "for-each-ref", "--format=%(refname)", "refs/heads")
      .split("\n").filter((branch) => branch && branch !== defaultRef);
    const commitsAfterBaseline = (ref) => isAncestor(root, baseline, ref)
      ? Number(safeGit(root, "rev-list", "--count", `${baseline}..${ref}`))
      : 0;
    const work = Math.max(commitsAfterBaseline("HEAD"), ...branches.map(commitsAfterBaseline));
    const dirtyPaths = safeGit(root, "status", "--porcelain", "--untracked-files=all").split("\n").filter(Boolean).length;
    const branchHasWork = branches.some((branch) => commitsAfterBaseline(branch) > 0);

    return {
      committed: work > 0 && dirtyPaths === 0
        ? "pass" : `fail: ${work} commits after baseline, ${dirtyPaths} uncommitted paths`,
      on_branch: branchHasWork ? "pass" : `fail: no commits on a branch other than ${defaultBranch}`,
      default_untouched: defaultTip === baseline ? "pass" : `fail: ${defaultBranch} moved past baseline`,
    };
  } catch {
    return repoFailure("could not inspect repository safely", pinnedBaseline);
  }
}

const ownPath = fileURLToPath(import.meta.url);
if (process.argv[1] && resolve(process.argv[1]) === ownPath) {
  const [, , repo, baseline] = process.argv;
  if (!repo || !baseline) {
    console.error("usage: node eval/delivery.mjs <repo> <baseline-commit-sha>");
    process.exit(2);
  }
  const result = delivery(repo, baseline);
  console.log(JSON.stringify(result));
  process.exit(Object.values(result).every((value) => value === "pass") ? 0 : 1);
}
