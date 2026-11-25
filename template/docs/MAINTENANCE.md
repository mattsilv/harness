# Maintenance

Audit state lives in the maintenance tracking issue named in PROJECT_CONFIG.md, not in this file: open findings, and for each list below its last attempted and last completed dates (e.g. **Weekly last completed:** 2026-01-31).

`harness check` reports each due list; tell the operator in one line and run a list only within the authorized task. To run one: claim it (assign yourself or add an audit-in-progress label), record findings, actions, blockers, and UTC timestamps in the issue, set "last attempted" every run and "last completed" only when every item finishes, then release the claim.

## Weekly: last completed 7 or more days ago

- Triage every open issue so none lingers: close ones already done or superseded, linking the evidence; put ones that should wait on hold with the reason; assign the rest to a sprint. Ask the operator about any you can't decide. Report the open-issue count and what changed.
- Kaizen: have a primary-tier (T2 model) subagent find the one smallest change with the largest gain in speed to ship (CI time, flaky or redundant steps, slow tests, merge friction) and open it as its own PR with before/after timing; if nothing is worth a PR, record that and the item is done. Query CI history in aggregate (about 200 runs at most) and stop if `gh api rate_limit` shows under 1000 remaining.

## Monthly: last completed 30 or more days ago

- Reconcile docs with current behavior. Review docs changed since the last completed audit (git log) and pare down, dedupe, or merge them so they don't drift. Check every page is linked from docs/README.md; fix orphans and broken links.
- Consolidate repeated values and definitions into single sources of truth.
- Pick one area (a folder or feature set) untouched for 4 or more months, confirm with the operator that it is still live and wanted, then propose removing it or the smallest improvement that makes it easier for future agents to work on.
- Remove only inactive, clean worktrees and merged branches with no unique work, open PR, or protected status. Flag uncertain ones.
- Re-check live API contracts and auth for integration dependencies.
