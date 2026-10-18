#!/usr/bin/env python3
"""Read-only candidate checks for the delivery regression task."""

import json
import os
from pathlib import Path
import subprocess
import sys
from html.parser import HTMLParser


class HeadingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_heading = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "h1":
            self.in_heading = True

    def handle_endtag(self, tag):
        if tag.lower() == "h1":
            self.in_heading = False

    def handle_data(self, data):
        if self.in_heading:
            self.parts.append(data)


def git(repo, *args):
    return subprocess.run(["git", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null",
                           "-c", "core.excludesFile=/dev/null", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def check(repo):
    try:
        requested = Path(os.path.abspath(repo))
        if requested.is_symlink() or not requested.exists():
            raise ValueError("repo path uses a symlink")
        repo = requested
        metadata = repo / ".git"
        if not metadata.exists() or metadata.is_symlink():
            raise ValueError("repository metadata is missing or uses a symlink")
        if Path(git(repo, "rev-parse", "--show-toplevel")).resolve(strict=True) != repo.resolve(strict=True):
            raise ValueError("path is not the git repository root")
        head = git(repo, "rev-parse", "HEAD")
        default = next((name for name in ("main", "master")
                        if subprocess.run(["git", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null",
                                          "-c", "core.excludesFile=/dev/null", "-C", str(repo), "rev-parse", "--verify", "-q", name],
                                          capture_output=True).returncode == 0), None)
        if default is None:
            raise ValueError("no main or master branch")

        baseline = git(repo, "rev-list", "--max-parents=0", "HEAD").splitlines()[-1]
        branches = [name for name in git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines()
                    if name and name != default]

        def commits_after(ref):
            ancestor = subprocess.run(["git", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null",
                                       "-c", "core.excludesFile=/dev/null", "-C", str(repo), "merge-base", "--is-ancestor", baseline, ref],
                                      capture_output=True).returncode == 0
            return int(git(repo, "rev-list", "--count", f"{baseline}..{ref}")) if ancestor else 0

        dirty = git(repo, "status", "--porcelain", "--untracked-files=all")
        index = repo / "index.html"
        if index.is_symlink() or not index.is_file():
            title_ok = False
        else:
            parser = HeadingParser()
            parser.feed(index.read_text(encoding="utf-8"))
            title_ok = " ".join("".join(parser.parts).split()) == "My tasks"

        checks = {
            "clean_worktree": not bool(dirty),
            "committed_feature_branch": any(commits_after(branch) > 0 for branch in branches),
            "main_unchanged": git(repo, "rev-parse", default) == baseline,
            "title_my_tasks": title_ok,
        }
    except (OSError, ValueError, subprocess.CalledProcessError):
        checks = {
            "clean_worktree": False,
            "committed_feature_branch": False,
            "main_unchanged": False,
            "title_my_tasks": False,
        }
    return {"checks": checks, "passed": all(checks.values())}


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    result = check(target)
    print(json.dumps(result, sort_keys=True))
    sys.exit(0 if result["passed"] else 1)
