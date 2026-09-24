#!/usr/bin/env node
// Harness evaluation: run fixed to-do checks against an app and count its source.
// Usage: node eval/check.mjs --task create|update <app-dir> [--url URL] [--model M]
//        [--effort E] [--tokens N] [--harness REV] [--out results.jsonl] [--shot FILE.png]
// Needs Node 22+ (built-in WebSocket) and a local Chrome or Chromium; no packages.
// Exits 0 only when every check passes. See EVAL.md.

import { spawn, execFileSync } from "node:child_process";
import { createServer } from "node:http";
import { existsSync, mkdtempSync, readFileSync, readdirSync, realpathSync, rmSync, statSync, appendFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, dirname, extname, isAbsolute, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const USAGE = "usage: node eval/check.mjs --task create|update <app-dir> [--url URL] [--model M] [--effort E] [--tokens N] [--harness REV] [--out FILE] [--shot FILE.png]";
const args = { model: "unverified", effort: "unverified", tokens: "unavailable" };
const rest = process.argv.slice(2);
while (rest.length) {
  const a = rest.shift();
  if (a.startsWith("--")) args[a.slice(2)] = rest.shift();
  else args.dir = a;
}
if (!["create", "update"].includes(args.task) || !args.dir || !existsSync(args.dir)) {
  console.error(USAGE);
  process.exit(2);
}
const dir = resolve(args.dir);

// ---- Counting: authored source only, whole-line comments, deterministic ----

const SOURCE_EXT = new Set([".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".html", ".css",
  ".scss", ".vue", ".svelte", ".py", ".sh"]);
const SKIP_DIRS = new Set(["node_modules", "dist", "build", "out", "coverage", ".git",
  ".harness", "playwright-report", "vendor", ".venv", "__pycache__", ".next", ".svelte-kit"]);
const SKIP_FILES = /(^|\/)(AGENTS\.md|CLAUDE\.md|PROJECT_CONFIG\.md|docs\/MAINTENANCE\.md|docs\/languages\/.*)$|\.min\.(js|css)$/;
const TEST_PATH = /(^|\/)(tests?|__tests__|e2e)\/|\.(test|spec)\.[^/]+$/;
const HASH_COMMENTS = new Set([".py", ".sh"]);

function listFiles(root) {
  const out = [];
  (function walk(d) {
    for (const name of readdirSync(d).sort()) {
      const p = join(d, name);
      if (statSync(p).isDirectory()) { if (!SKIP_DIRS.has(name)) walk(p); }
      else out.push(relative(root, p).split("\\").join("/"));
    }
  })(root);
  return out;
}

function count(root) {
  const c = { files: 0, source_lines: 0, comment_lines: 0, test_lines: 0 };
  for (const f of listFiles(root)) {
    const ext = extname(f);
    if (!SOURCE_EXT.has(ext) || SKIP_FILES.test(f)) continue;
    c.files++;
    for (const raw of readFileSync(join(root, f), "utf8").split("\n")) {
      const line = raw.trim();
      if (!line) continue;
      c.source_lines++;
      if (TEST_PATH.test(f)) c.test_lines++;
      if (/^(\/\/|\/\*|\*|<!--)/.test(line) || (HASH_COMMENTS.has(ext) && line.startsWith("#"))) c.comment_lines++;
    }
  }
  return c;
}

// ---- Browser: headless Chrome over the DevTools protocol ----

function findChrome() {
  const candidates = [process.env.CHROME_PATH,
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium"];
  for (const name of ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]) {
    try { candidates.push(execFileSync("which", [name], { encoding: "utf8" }).trim()); } catch {}
  }
  const found = candidates.find((p) => p && existsSync(p));
  if (!found) throw new Error("no Chrome found; set CHROME_PATH");
  return found;
}

async function launch() {
  const profile = mkdtempSync(join(tmpdir(), "harness-eval-"));
  const proc = spawn(findChrome(), ["--headless=new", "--remote-debugging-port=0",
    `--user-data-dir=${profile}`, "--no-first-run", "--no-default-browser-check", "about:blank"],
  { stdio: ["ignore", "ignore", "pipe"] });
  const kill = async () => {
    if (proc.exitCode === null && proc.signalCode === null) {
      const exited = new Promise((ok) => proc.once("exit", ok));
      proc.kill();
      await exited;
    }
    rmSync(profile, { recursive: true, force: true, maxRetries: 5 });
  };
  try {
    return await connect(proc, kill);
  } catch (e) {
    await kill();
    throw e;
  }
}

async function connect(proc, kill) {
  const wsUrl = await new Promise((ok, fail) => {
    let err = "";
    setTimeout(() => fail(new Error("Chrome did not start within 15s")), 15000).unref();
    proc.stderr.on("data", (d) => {
      err += d;
      const m = err.match(/DevTools listening on (ws:\/\/\S+)/);
      if (m) ok(m[1]);
    });
    proc.on("exit", () => fail(new Error(`Chrome exited: ${err.slice(-500)}`)));
  });
  const ws = new WebSocket(wsUrl);
  await new Promise((ok, fail) => { ws.onopen = ok; ws.onerror = () => fail(new Error("DevTools connection failed")); });
  let id = 0;
  const pending = new Map();
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    const p = pending.get(msg.id);
    if (!p) return;
    pending.delete(msg.id);
    msg.error ? p.fail(new Error(msg.error.message)) : p.ok(msg.result);
  };
  const raw = (method, params = {}, sessionId) => new Promise((ok, fail) => {
    pending.set(++id, { ok, fail });
    ws.send(JSON.stringify({ id, method, params, sessionId }));
  });
  const { targetId } = await raw("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await raw("Target.attachToTarget", { targetId, flatten: true });
  const send = (method, params) => raw(method, params, sessionId);
  const close = async () => { ws.close(); await kill(); };
  return { send, close };
}

// Page-side helpers, found by role and accessible name so any framework's markup works.
const HELPERS = `(() => {
  const vis = (el) => el && (el.checkVisibility ? el.checkVisibility() : el.offsetParent !== null);
  const name = (el) => (el.getAttribute("aria-label") || el.title || el.textContent || el.value || "").trim();
  const all = (sel, root = document) => [...root.querySelectorAll(sel)].filter(vis);
  const input = () => all('input:not([type]), input[type=text], input[type=search], textarea')[0];
  const labels = (text) => all("body *").filter((el) =>
    el.textContent.trim() === text && ![...el.children].some((c) => c.textContent.trim() === text));
  const toggleEl = (r) => r.querySelector('input[type=checkbox], [role=checkbox]') ||
    [...r.querySelectorAll("button")].find((b) => /complete|done|toggle|check|mark/i.test(name(b)));
  const delEl = (r) => [...r.querySelectorAll("button, [role=button]")].find((b) => /delete|remove|^(×|✕|x)$/i.test(name(b)));
  // The nearest ancestor of the task's text that holds the control find() looks for, so a
  // <label> wrapping only the checkbox and text doesn't hide a sibling delete button. It stops
  // once it spans more than one task, so it never borrows another task's control.
  const row = (text, find = (r) => r.querySelector('input[type=checkbox], [role=checkbox], button')) => {
    for (let el of labels(text)) {
      for (; el && el !== document.body; el = el.parentElement) {
        if (el.querySelectorAll('input[type=checkbox], [role=checkbox]').length > 1) break;
        if (find(el)) return el;
      }
    }
    return null;
  };
  return window.__ev = {
    hasInput: () => !!input(),
    focus: () => { const i = input(); i.focus(); i.select && i.select(); return !!i; },
    clickAdd: () => { const b = all("button").find((b) => /^(\\+|add|save|create|submit)/i.test(name(b))); b && b.click(); return !!b; },
    rows: () => all('input[type=checkbox], [role=checkbox]').length,
    shown: (t) => !!row(t),
    done: (t) => {
      const r = row(t, toggleEl), el = toggleEl(r);
      if (el && el.type === "checkbox") return el.checked;
      if (el && el.hasAttribute("aria-checked")) return el.getAttribute("aria-checked") === "true";
      if (el && el.hasAttribute("aria-pressed")) return el.getAttribute("aria-pressed") === "true";
      const l = labels(t)[0];
      return /line-through/.test(getComputedStyle(l).textDecorationLine) || /complete|done/i.test(r.className);
    },
    toggle: (t) => { toggleEl(row(t, toggleEl)).click(); },
    del: (t) => { delEl(row(t, delEl)).click(); },
    filter: (f) => {
      const re = new RegExp("^" + f + "\\\\b", "i");
      for (const sel of all("select")) {
        const o = [...sel.options].find((o) => re.test(o.textContent.trim()));
        if (o) { sel.value = o.value; sel.dispatchEvent(new Event("input", { bubbles: true })); sel.dispatchEvent(new Event("change", { bubbles: true })); return; }
      }
      all('button, a, [role=tab], [role=radio], label').find((b) => re.test(name(b))).click();
    },
  };
})()`;

// ---- The fixed checks ----

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function run(url, task) {
  const { send, close } = await launch();
  const results = {};
  const ev = async (expr) => {
    const r = await send("Runtime.evaluate", { expression: `(window.__ev || ${HELPERS}).${expr}`, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description?.split("\n")[0] || "page error");
    return r.result.value;
  };
  const settle = async () => {
    for (let i = 0; i < 50; i++) {
      await sleep(100);
      try { if (await ev("hasInput()")) return; } catch {}
    }
    throw new Error("no text input appeared");
  };
  const load = async (reload) => {
    await send(reload ? "Page.reload" : "Page.navigate", reload ? {} : { url });
    await sleep(200);
    await send("Runtime.evaluate", { expression: "delete window.__ev" });
    await settle();
  };
  const key = (type) => send("Input.dispatchKeyEvent", { type, key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, text: type === "keyDown" ? "\r" : undefined });
  const add = async (text) => {
    const before = await ev("rows()");
    await ev("focus()");
    await send("Input.insertText", { text });
    await key("keyDown"); await key("keyUp");
    await sleep(500);
    if ((await ev("rows()")) === before && text.trim()) { await ev("clickAdd()"); await sleep(300); }
  };
  const act = async (expr) => { await ev(expr); await sleep(200); };
  const q = (s) => JSON.stringify(s);
  const check = async (name, fn) => {
    try { const ok = await fn(); results[name] = ok ? "pass" : "fail"; }
    catch (e) { results[name] = `fail: ${e.message}`; }
  };

  try {
    await send("Page.enable");
    await check("loads", async () => { await load(); return true; });
    if (task === "update") {
      // The update starts from eval/fixture, so its storage format is known.
      await check("keeps_saved_tasks", async () => {
        await send("Runtime.evaluate", { expression: `localStorage.setItem("todos", ${q(JSON.stringify([
          { id: 1, text: "Saved open", done: false }, { id: 2, text: "Saved done", done: true }]))})` });
        await load(true);
        return await ev(`shown("Saved open")`) && await ev(`shown("Saved done")`) &&
          !(await ev(`done("Saved open")`)) && await ev(`done("Saved done")`);
      });
    }
    await check("add", async () => { await add("Buy milk"); return ev(`shown("Buy milk")`); });
    await check("reject_blank", async () => {
      const before = await ev("rows()");
      await add("   ");
      return (await ev("rows()")) === before;
    });
    await check("toggle", async () => {
      await add("Walk dog");
      await act(`toggle("Buy milk")`);
      const on = await ev(`done("Buy milk")`) && !(await ev(`done("Walk dog")`));
      await act(`toggle("Buy milk")`);
      const off = !(await ev(`done("Buy milk")`));
      await act(`toggle("Buy milk")`);
      return on && off;
    });
    await check("delete", async () => {
      await add("Delete me");
      await act(`del("Delete me")`);
      return !(await ev(`shown("Delete me")`)) && await ev(`shown("Buy milk")`);
    });
    await check("persist_reload", async () => {
      await load(true);
      return await ev(`shown("Buy milk")`) && await ev(`done("Buy milk")`) &&
        await ev(`shown("Walk dog")`) && !(await ev(`done("Walk dog")`)) && !(await ev(`shown("Delete me")`));
    });
    if (task === "update") {
      await check("filter_active", async () => {
        await act(`filter("Active")`);
        return await ev(`shown("Walk dog")`) && !(await ev(`shown("Buy milk")`));
      });
      await check("filter_completed", async () => {
        await act(`filter("Completed")`);
        return await ev(`shown("Buy milk")`) && !(await ev(`shown("Walk dog")`));
      });
      await check("filter_all", async () => {
        await act(`filter("All")`);
        return await ev(`shown("Buy milk")`) && await ev(`shown("Walk dog")`);
      });
    }
    if (args.shot) {
      // The final state (one done task, one open), at a fixed size so runs compare side by side.
      await send("Emulation.setDeviceMetricsOverride", { width: 1024, height: 768, deviceScaleFactor: 1, mobile: false });
      await sleep(300);
      const { data } = await send("Page.captureScreenshot", { format: "png" });
      writeFileSync(args.shot, Buffer.from(data, "base64"));
    }
  } finally {
    await close();
  }
  return results;
}

function serve(root) {
  const types = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml" };
  const server = createServer((req, res) => {
    let p = join(root, decodeURIComponent(new URL(req.url, "http://x").pathname));
    const rel = relative(root, p);
    if (rel.startsWith("..") || isAbsolute(rel)) { res.writeHead(403).end(); return; }
    if (existsSync(p) && statSync(p).isDirectory()) p = join(p, "index.html");
    if (!existsSync(p)) { res.writeHead(404).end(); return; }
    res.writeHead(200, { "content-type": types[extname(p)] || "application/octet-stream" }).end(readFileSync(p));
  });
  return new Promise((ok) => server.listen(0, "127.0.0.1", () => ok(server)));
}

function gitRev(cwd, ...paths) {
  try {
    const rev = execFileSync("git", ["-C", cwd, "log", "-1", "--format=%h", "--", ...paths], { encoding: "utf8" }).trim();
    const dirty = execFileSync("git", ["-C", cwd, "status", "--porcelain", "--", ...paths], { encoding: "utf8" }).trim();
    return rev ? rev + (dirty ? "+dirty" : "") : "uncommitted";
  } catch { return "unknown"; }
}

// Delivery: work committed on a branch, default branch left alone. A run repo starts with one
// baseline commit on its default branch (EVAL.md); reported apart from the score and exit code.
function delivery(cwd) {
  const git = (...a) => execFileSync("git", ["-C", cwd, ...a], { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
  // Only a run repo's own root counts, not an app inside some other checkout.
  try { if (realpathSync(git("rev-parse", "--show-toplevel")) !== realpathSync(cwd) || !git("rev-parse", "HEAD")) throw 0; } catch { return { committed: "unverified", on_branch: "unverified", default_untouched: "unverified" }; }
  const base = git("rev-list", "--max-parents=0", "HEAD").split("\n").pop();
  const def = ["main", "master"].find((b) => { try { return git("rev-parse", "--verify", "-q", b); } catch { return false; } });
  const branch = git("branch", "--show-current") || "detached";
  const ahead = Number(git("rev-list", "--count", `${base}..HEAD`));
  const dirty = git("status", "--porcelain").split("\n").filter(Boolean).length;
  return {
    committed: ahead && !dirty ? "pass" : `fail: ${ahead} commits after baseline, ${dirty} uncommitted paths`,
    on_branch: !def ? "unverified" : branch !== def ? "pass" : `fail: on ${def}`,
    default_untouched: !def ? "unverified" : git("rev-parse", def) === base ? "pass" : `fail: ${def} moved past baseline`,
  };
}

const here = dirname(fileURLToPath(import.meta.url));
const harnessFile = join(dir, ".harness", "version");
// The page is <app-dir>/index.html, or the only index.html elsewhere in the app (e.g. src/).
function entry() {
  if (existsSync(join(dir, "index.html"))) return "";
  const found = listFiles(dir).filter((f) => basename(f) === "index.html" && !TEST_PATH.test(f));
  if (found.length === 1) { console.error(`serving ${found[0]}`); return dirname(found[0]) + "/"; }
  console.error(`no single index.html in ${dir} (found: ${found.join(", ") || "none"}); pass --url`);
  process.exit(2);
}
const server = args.url ? null : await serve(dir);
const url = args.url || `http://127.0.0.1:${server.address().port}/${entry()}`;
let checks;
try { checks = await run(url, args.task); } finally { server?.close(); }

const passed = Object.values(checks).filter((v) => v === "pass").length;
const record = {
  date: new Date().toISOString().slice(0, 10),
  task: args.task,
  app: basename(dir),
  harness: args.harness || (existsSync(harnessFile) ? `v${readFileSync(harnessFile, "utf8").trim()}` : "unknown"),
  fixture: gitRev(here, "check.mjs", "fixture"), // the evaluator's own revision, not stored results
  model: args.model,
  effort: args.effort,
  tokens: args.tokens,
  checks,
  passed: `${passed}/${Object.keys(checks).length}`,
  delivery: delivery(dir),
  counts: count(dir),
};
for (const [k, v] of Object.entries({ ...checks, ...record.delivery })) console.error(`${v === "pass" ? "PASS" : v === "unverified" ? "----" : "FAIL"}  ${k}${v === "pass" ? "" : `  (${v})`}`);
console.log(JSON.stringify(record));
if (args.out) appendFileSync(args.out, JSON.stringify(record) + "\n");
process.exit(passed === Object.keys(checks).length ? 0 : 1);
