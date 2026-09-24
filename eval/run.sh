#!/usr/bin/env bash
# Harness evaluation: one fresh headless run of an EVAL.md task, then its check.
# Usage: eval/run.sh claude|opencode create|update <run-dir> [model]
# Start runs one after another: parallel OpenCode sessions fail on a locked database.
# Writes <run-dir>/ (the run repo) and <run-dir>.{events.jsonl,stderr,usage.json,report.md,
# check.json,png} beside it. See EVAL.md.
set -euo pipefail

agent=${1:?agent}; task=${2:?task}; run=${3:?run-dir}; model=${4:-}
case $agent in claude|opencode) ;; *) echo "run.sh: unknown agent $agent" >&2; exit 2 ;; esac
here=$(cd "$(dirname "$0")" && pwd)
[ -e "$run" ] && { echo "run.sh: $run exists" >&2; exit 2; }
heading=$(echo "$task" | awk '{print toupper(substr($0, 1, 1)) substr($0, 2)}')
prompt=$(sed -n "/^## $heading prompt/,/^## /s/^> //p" "$here/../EVAL.md")
[ -n "$prompt" ] || { echo "run.sh: no ${task} prompt in EVAL.md" >&2; exit 2; }

# Run repo: the harness under test, EVAL.md's setup values, one baseline commit on main.
mkdir -p "$run"
[ "$task" = update ] && cp "$here/fixture/index.html" "$run/"
git -C "$run" init -q -b main
(cd "$run" && HARNESS_SYNC_SOURCE=${HARNESS_SYNC_SOURCE:-$here/../template} harness init >/dev/null)
sed -i.bak -E \
  -e 's/^- \*\*Stack:\*\*.*/- **Stack:** A single static HTML\/JS page with localStorage; no build step and no server./' \
  -e 's/^- \*\*Maintenance tracking issue:\*\*.*/- **Maintenance tracking issue:** None./' \
  -e 's/^- \*\*Merge policy:\*\*.*/- **Merge policy:** `on-request`./' \
  -e 's/^- \*\*Secrets:\*\*.*/- **Secrets:** None needed./' \
  -e 's/^- \*\*Secrets location:\*\*.*/- **Secrets location:** None needed./' \
  "$run/PROJECT_CONFIG.md" && rm "$run/PROJECT_CONFIG.md.bak"
if grep -qi "set during setup" "$run/PROJECT_CONFIG.md"; then echo "run.sh: setup values left unset" >&2; exit 2; fi
git -C "$run" add -A
git -C "$run" -c user.name=eval -c user.email=eval@example.invalid commit -qm "Baseline: harness v$(cat "$run/.harness/version") installed, setup values recorded"

# The agent: a fresh session, project settings only, no user config or MCP servers.
start=$(date +%s)
case $agent in
  claude)
    model=${model:-opus}; cli="Claude Code $(claude --version | cut -d' ' -f1)"
    (cd "$run" && claude -p "$prompt" --model "$model" --effort medium --permission-mode bypassPermissions \
      --setting-sources project --strict-mcp-config --no-chrome --output-format stream-json --verbose) \
      > "$run.events.jsonl" 2> "$run.stderr" || true
    node -e '
      const lines = require("fs").readFileSync(process.argv[1], "utf8").split("\n").filter(Boolean).map(JSON.parse);
      const r = lines.findLast((l) => l.type === "result") || {};
      const texts = lines.filter((l) => l.type === "assistant").flatMap((l) => l.message.content).filter((c) => c.type === "text");
      const u = Object.values(r.modelUsage || {});
      const sum = (k) => u.reduce((n, m) => n + (m[k] || 0), 0);
      const tokens = sum("inputTokens") + sum("outputTokens") + sum("cacheReadInputTokens") + sum("cacheCreationInputTokens");
      const subagents = lines.filter((l) => l.type === "assistant").flatMap((l) => l.message.content)
        .filter((c) => c.type === "tool_use" && ["Agent", "Task"].includes(c.name)).map((c) => c.input.model || c.input.subagent_type || "default");
      console.log(JSON.stringify({ cli: process.argv[2], models: Object.keys(r.modelUsage || {}), effort: "medium (requested; not echoed)",
        cost_usd: r.total_cost_usd ?? "unavailable", cost_basis: "list price", tokens_total: tokens || "unavailable",
        turns: r.num_turns ?? "unavailable", duration_s: r.duration_ms ? Math.round(r.duration_ms / 1000) : "unavailable", subagents }));
      require("fs").writeFileSync(process.argv[3], r.result || texts.at(-1)?.text || "");
    ' "$run.events.jsonl" "$cli" "$run.report.md" > "$run.usage.json"
    ;;
  opencode)
    model=${model:-opencode-go/deepseek-v4.1-flash}; cli="OpenCode $(opencode --version)"
    empty=$(mktemp -d)  # no user config, so only the project's files apply
    (cd "$run" && XDG_CONFIG_HOME=$empty OPENCODE_DISABLE_CLAUDE_CODE=1 opencode run "$prompt" --model "$model" \
      --agent build --pure --auto --format json) > "$run.events.jsonl" 2> "$run.stderr" || true
    sid=$(node -e 'const l = require("fs").readFileSync(process.argv[1], "utf8").split("\n").find(Boolean); console.log(l ? JSON.parse(l).sessionID : "")' "$run.events.jsonl")
    [ -n "$sid" ] && XDG_CONFIG_HOME=$empty opencode export "$sid" > "$run.export.json" 2>/dev/null || echo '{}' > "$run.export.json"
    node -e '
      const fs = require("fs"), [ev, exp, cli, rep] = process.argv.slice(1);
      const lines = fs.readFileSync(ev, "utf8").split("\n").filter(Boolean).map(JSON.parse);
      const i = JSON.parse(fs.readFileSync(exp, "utf8")).info || {}, t = i.tokens;
      const tools = lines.filter((e) => e.type === "tool_use").map((e) => e.part.tool);
      const texts = lines.filter((e) => e.type === "text").map((e) => e.part.text);
      console.log(JSON.stringify({ cli, models: i.model ? [`${i.model.providerID}/${i.model.id}`] : [], effort: i.model?.variant || "default",
        cost_usd: i.cost ?? "unavailable", cost_basis: "provider-reported", tokens_total: t ? t.input + t.output + t.reasoning + t.cache.read + t.cache.write : "unavailable",
        turns: lines.filter((e) => e.type === "step_finish").length || "unavailable",
        duration_s: i.time ? Math.round((i.time.updated - i.time.created) / 1000) : "unavailable", subagents: tools.filter((x) => x === "task") }));
      fs.writeFileSync(rep, texts.at(-1) || "");
    ' "$run.events.jsonl" "$run.export.json" "$cli" "$run.report.md" > "$run.usage.json"
    rm -rf "$empty"
    ;;
esac
echo "$(basename "$run"): $agent finished in $(( $(date +%s) - start ))s" >&2

tokens=$(node -e 'console.log(JSON.parse(require("fs").readFileSync(process.argv[1], "utf8")).tokens_total)' "$run.usage.json")
node "$here/check.mjs" --task "$task" "$run" --model "$model" --effort "$([ "$agent" = claude ] && echo medium || echo default)" \
  --tokens "$tokens" --shot "$run.png" > "$run.check.json"
