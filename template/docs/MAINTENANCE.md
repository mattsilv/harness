# Maintenance

Audit state lives in the maintenance tracking issue named in PROJECT_CONFIG.md, not in this file: open findings, and for each list below its last attempted and last completed dates (e.g. **Weekly last completed:** 2026-01-31).

At session start, check that issue. A list is due when its heading's interval has passed since it last completed, or, if it never completed, since the harness was installed (the first commit of .harness/). Claim a due list (assign yourself or add an audit-in-progress label), run it after the current task, delegating the checks to T3 subagents (PROJECT_CONFIG.md) and reviewing their findings yourself, and surface overdue or blocked work in one line. Retry incomplete audits next session. Record findings, actions, blockers, and UTC timestamps in the tracking issue; update "last attempted" every run and "last completed" only when every check in that list finishes. Release the claim when done.

## Weekly: last completed 7 or more days ago

- Triage every open issue so none lingers: close ones already done or superseded, linking the evidence; put ones that should wait on hold with the reason; assign the rest to a sprint. Ask the operator about any you can't decide. Report the open-issue count and what changed.

## Monthly: last completed 30 or more days ago

- Reconcile docs with current behavior. Review docs changed since the last completed audit (git log) and pare down, dedupe, or merge them so they don't drift. Check every page is linked from docs/README.md; fix orphans and broken links.
- Consolidate repeated values and definitions into single sources of truth.
- Pick one area (a folder or feature set) untouched for 4 or more months, confirm with the operator that it is still live and wanted, then propose removing it or the smallest improvement that makes it easier for future agents to work on.
- Remove only inactive, clean worktrees and merged branches with no unique work, open PR, or protected status. Flag uncertain ones.
- Re-check live API contracts and auth for integration dependencies.
