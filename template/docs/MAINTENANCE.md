# Maintenance

Audit state (last attempted, last completed, open findings) lives in the maintenance tracking issue named in PROJECT_CONFIG.md, not in this file.

At session start, check that issue. If the audit last completed 30 or more days ago, or never completed and the harness was installed (the first commit of .harness/) that long ago, claim it (assign yourself or add an audit-in-progress label), run it after the current task, delegating the checks to T3 subagents (PROJECT_CONFIG.md) and reviewing their findings yourself, and surface overdue or blocked work in one line. Retry incomplete audits next session.

- Reconcile docs with current behavior. Review docs changed since the last completed audit (git log) and pare down, dedupe, or merge them so they don't drift. Check every page is linked from docs/README.md; fix orphans and broken links.
- Consolidate repeated values and definitions into single sources of truth.
- Pick one area (a folder or feature set) untouched for 4 or more months, confirm with the operator that it is still live and wanted, then propose removing it or the smallest improvement that makes it easier for future agents to work on.
- Remove only inactive, clean worktrees and merged branches with no unique work, open PR, or protected status. Flag uncertain ones.
- Review open issues older than 30 days and record a next action or deferral reason. Age triggers review, not closure or priority.
- Re-check live API contracts and auth for integration dependencies.
- Record findings, actions, blockers, and UTC timestamps in the tracking issue. Update "last attempted" every run and "last completed" only when every check finishes. Release the claim when done.

Only a full audit resets the monthly clock.
