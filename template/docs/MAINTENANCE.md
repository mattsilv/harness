# Maintenance

Audit state (last attempted, last completed, open findings) lives in the maintenance tracking issue named in PROJECT_CONFIG.md, not in this file.

At session start, check that issue. If the audit has never completed or last completed 7 or more days ago, claim it (assign yourself or add an audit-in-progress label), run it in a background subagent or after the current task, and surface overdue or blocked work in one line. Retry incomplete audits next session.

- Reconcile docs with current behavior; remove stale or duplicate guidance; fix broken references.
- Consolidate repeated values and definitions into single sources of truth.
- Remove only inactive, clean worktrees and merged branches with no unique work, open PR, or protected status. Flag uncertain ones.
- Review open issues older than 7 days and record a next action or deferral reason. Age triggers review, not closure or priority.
- Re-check live API contracts and auth for integration dependencies.
- Record findings, actions, blockers, and UTC timestamps in the tracking issue. Update "last attempted" every run and "last completed" only when every check finishes. Release the claim when done.

Only a full audit resets the weekly clock.
