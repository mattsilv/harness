# Harness review

You are reviewing this harness to make it lighter. Run this when a new frontier model
ships, or once a quarter. Everything you need is in this repo; the operator will react
to your report.

## Goal

The fewest rules that still prevent real failures by current frontier coding agents.
Rules drift in two ways: they pile up after incidents, and they outlive the model
weakness that justified them. Your job is to find both.

## Read first

1. `README.md`, for how the files are loaded.
2. Everything in `template/`, the only text projects receive.
3. The comment under each rule in `template/AGENTS.md`, and `RATIONALE.md` for the
   other files, for why each rule exists.
4. Your vendor's current prompting guide for the model you are. Guidance changes
   between generations. For example, newer models over-follow emphatic wording
   (capitals, "CRITICAL", "NEVER"), and older harnesses shout. Cite the guide
   where it drives a change.
5. Any evidence the operator attaches: session transcripts, retros, incident notes.
   Don't go looking outside this repo and what's attached. If there's no evidence,
   say so and fall back to self-report.

## Test each rule

Grade each top-level bullet; split a bullet into rows only where its clauses get
different verdicts. For every rule, ask:
**would a current frontier coding agent do the wrong thing without it?**

- **Cut** it if it restates default behavior of capable models, or if its rationale
  is gone.
- **Move** it to `PROJECT_CONFIG.md` if it's a project-specific value or preference.
- **Move** it to an on-demand file (`docs/languages/`, or a new linked file with an
  explicit trigger) if it only applies to some tasks.
- **Rewrite** it if it's right but wordy, emphatic, vague, or duplicated elsewhere.
- **Keep** it if it prevents a failure you'd plausibly make, or one the evidence shows.

Weigh evidence over self-report. A transcript showing the failure, or a rationale
naming an incident, outweighs your opinion of what you'd do. Say which kind of evidence
each decision rests on. A rule whose rationale is "Unknown" or "Incident not recorded" is presumed
cuttable. Cite the vendor guide wherever it informs a verdict, including a keep.

Revisit the previous review's changes against any failure evidence, and note in the new
log row whether any need revision: "unknown" without evidence, "n/a" if no earlier
review changed rules. Run [EVAL.md](EVAL.md) twice per task on the current and the proposed
harness, scored by [eval/check.mjs](eval/check.mjs), and cite the stored results in
[eval/runs/](eval/runs/) as evidence.

## Don't cut

- The Autonomy list of actions that need operator approval, and the Security and
  Secrets rules.
  These are safety boundaries set by the operator, not crutches for weak models.
  You may propose clearer wording, never removal or loosening.
- Anything the `harness` CLI parses: "Set during setup", the `**Merge policy:**` and
  `**Maintenance tracking issue:**` labels, and the "## <List>: ... N or more days ago"
  headings in `docs/MAINTENANCE.md` with their "<List> last completed:" fields in the
  tracking issue. Changing those needs a matching change to the `harness` CLI.

## Also check

- **Model names:** none in `template/AGENTS.md`. Model choices belong only in
  `PROJECT_CONFIG.md`.
- **Contradictions and duplicates** across the template files.
- **Public-safe:** no PII, hostnames, or project specifics.

## Deliver

1. A table: rule, verdict (keep/cut/move/rewrite), one-line reason, evidence type.
2. A PR (or patch) against `template/` and `RATIONALE.md`, with rationale comments
   and lines removed or updated to match, and each reviewed rule's `review:` line
   set to your verdict, confidence, model, and date. Net size must not grow unless the PR says why.
   Report the before/after word count of `template/AGENTS.md`.
3. A row appended to the log below.

## Log

| Date | Reviewer model | AGENTS.md words (before → after) | Notes |
|---|---|---|---|
| 2026-09-23 | — | 675 → 675 | Moved from a Google Doc to this repo; split Python rule into docs/languages/. No review yet. |
| 2026-09-23 | — (eval pilot; reviews by Sonnet 5 and Haiku 4.5) | 738 → 738 | First [EVAL.md](EVAL.md) run on v8: Claude Code/Opus, OpenCode/DeepSeek V4.1 Flash, and Codex/GPT-6 Sol, 2 runs per task, all 12 passed every check. OpenCode left its work uncommitted in 4/4 runs. Cost: $2.62 at Claude list price (subscription), $0.08 OpenCode Go, Codex unavailable, Jev $0.0013. No rules changed; previous review n/a. [Details](eval/runs/2026-09-23-v8.md). |
| 2026-10-18 | GPT-6 Luna (requested), high; independent Luna review | 1235 → 1235 | Delivery-helper smoke test: all 12 runs passed corrected functional and delivery checks; baseline failure did not recur. Reject template adoption: +104 instruction bytes, +165.426 seconds total candidate wall time, no demonstrated gain. Previous template changes: unknown individually. [Evidence and scoring correction](eval/runs/2026-10-18-delivery/README.md). |
| 2026-10-29 | Operator-directed change; independent agent review | 1255 → 1220 | #71: portable adapters and single-task completion; scoped policy edit, not a full rule-removal review. 64 fixture tests, fresh init, clean v41 upgrade, edited-config recovery, and real-project check/diff passed; independent review found no blockers. Added completion/handoff evaluation scenarios in EVAL.md; live comparative behavior is unverified. Previous changes: not reassessed in this scoped change. |
| 2026-11-10 | Claude Fable 5.2; transcript mining by six Sonnet 5.5 subagents | 1220 → 1120 | Evidence-led partial review, not a full per-rule pass: about 60 Claude Code and 10 Codex sessions from 14 days across 7 projects. Friction was mostly in scripts (#73); rule changes in #74 cut or shrank 7 rules, rewrote 6, added delivery-15. No eval run (operator runs evals on request only). Rules with "Unknown" rationale and no transcript evidence were left for the full review. #71's changes: single-task completion held (maintenance no longer expands scope unasked, apart from two sessions); delegation-4's adapter pointer was a no-op in Codex and is cut. |
| 2026-11-10 | Claude Fable 5.2 | 1120 → 970 | Full per-rule pass, 48 rules graded, 43 remain (#77). Evidence: the same 14-day transcript set as the row above; self-report where it was silent. No eval run (operator runs evals on request only), so behavior under the shorter rules is unverified. Cut core-2 and models-2; merged testing-2 into testing-1 and delivery-12 into delivery-11; moved delivery-5 to docs/CI.md; shortened config-2, impl-3, delivery-9, docs-1, docs-3, delegation-1. Three changes reverse earlier operator decisions (delivery-5, delivery-12, docs-3) and are listed apart in the PR. Kept despite "Unknown" rationale: impl-2, testing-3, testing-4 (operator decisions, no contrary evidence), process-1, process-2, ui-2, testing-5 (transcript support). Also checked: no model names in AGENTS.md; no contradictions across template files; public-safe. Left alone: PROJECT_CONFIG's model-tier and frontend blocks (values projects have edited; trimming them conflicts on apply for little gain), the empty Claude Code adapter (kept on purpose in #76), and docs/languages/python.md (repeats PROJECT_CONFIG, but deleting a file costs every project a manual cleanup). Earlier same-day changes (#74): no failure evidence yet. |
