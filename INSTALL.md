# Install the harness into a repo

Instructions for a coding agent. The operator only needs to say "Follow INSTALL.md
in github.com/mattsilv/harness" from inside the target repo. Works for new and
existing repos; nothing is overwritten.

1. **Get the `harness` CLI.** If `command -v harness` finds nothing:
   `git clone https://github.com/mattsilv/harness ~/gh/harness` (or `git -C ~/gh/harness pull`
   if it exists), then `ln -sf ~/gh/harness/harness ~/.local/bin/harness`.
2. **Branch.** Work on a new branch (or worktree) from a freshly fetched default branch.
3. **Run `harness init`** at the repo root.
4. **Merge existing files.** For each file init reports as already existing, merge the
   harness version from `.harness/base/<path>` into it by hand. Keep project-specific
   content; remove anything the harness duplicates. Where they contradict, don't
   choose: list the conflicts for the operator.
5. **Claude Code:** make sure `CLAUDE.md` contains an `@AGENTS.md` line.
6. **Configure.** Ask the operator for every `PROJECT_CONFIG.md` value marked "Set during
   setup", and for any default that doesn't match this repo (stack, secrets project).
   Record the answers. Don't guess. `auto` merge only takes effect once the default
   branch requires a CI status check. If the repo has no CI or no such rule, say so and
   offer to add a CI workflow and a ruleset requiring it (a permission change: ask
   first), or record `on-request`.
   The ruleset should require the check but not that branches be up to date: that
   setting makes every merge re-run every open PR's check, and CI runs again on the
   default branch after each merge anyway. Also enable the repo setting "Allow
   auto-merge", which `auto` needs to merge green PRs without anyone waiting.
7. **Languages.** If the repo uses a language with no `docs/languages/<language>.md`,
   tell the operator. Don't write one unasked.
8. **Ship.** Commit only what init created or you changed (`AGENTS.md`, `CLAUDE.md`,
   `PROJECT_CONFIG.md`, `docs/MAINTENANCE.md`, `docs/languages/`, `.harness/`), not
   unrelated files already in `docs/`, and open a PR. Merge per the merge policy just recorded.
9. **Verify.** `harness check` prints nothing, except possibly a notice that the
   maintenance audit has never run.
10. **Session hook (once per machine).** If `harness check` doesn't already run at
    session start, tell the operator the README's "Session start" line. Don't edit
    global settings unasked.
