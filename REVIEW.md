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
3. `RATIONALE.md`, for why each rule exists.
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

Weigh evidence over self-report. A transcript showing the failure, or `RATIONALE.md`
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
- Anything `harness-sync` parses: "Set during setup", the `**Merge policy:**` and
  `**Maintenance tracking issue:**` labels, and "N or more days ago" in
  `docs/MAINTENANCE.md`. Changing those needs a matching `harness-sync` change.

## Also check

- **Model names:** none in `template/AGENTS.md`. Model choices belong only in
  `PROJECT_CONFIG.md`.
- **Contradictions and duplicates** across the template files.
- **Public-safe:** no PII, hostnames, or project specifics.

## Deliver

1. A table: rule, verdict (keep/cut/move/rewrite), one-line reason, evidence type.
2. A PR (or patch) against `template/` and `RATIONALE.md`, with rationale lines
   removed or updated to match. Net size must not grow unless the PR says why.
   Report the before/after word count of `template/AGENTS.md`.
3. A row appended to the log below.

## Log

| Date | Reviewer model | AGENTS.md words (before → after) | Notes |
|---|---|---|---|
| 2026-09-23 | — | 675 → 675 | Moved from a Google Doc to this repo; split Python rule into docs/languages/. No review yet. |
| 2026-09-23 | — (eval pilot; reviews by Sonnet 5 and Haiku 4.5) | 738 → 738 | First [EVAL.md](EVAL.md) run on v8: Claude Code/Opus, OpenCode/DeepSeek V4.1 Flash, and Codex/GPT-6 Sol, 2 runs per task, all 12 passed every check. OpenCode left its work uncommitted in 4/4 runs. Cost: $2.62 at Claude list price (subscription), $0.08 OpenCode Go, Codex unavailable, Jev $0.0013. No rules changed; previous review n/a. [Details](eval/runs/2026-09-23-v8.md). |
