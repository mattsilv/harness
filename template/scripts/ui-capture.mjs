#!/usr/bin/env node
// Batch capture and freshness checking; see docs/FRONTEND.md.
import { readFile, writeFile, mkdir, readdir, unlink } from 'node:fs/promises';
import { resolve, dirname, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { parseArgs } from 'node:util';

const { values: args } = parseArgs({ options: {
  driver: { type: 'string' }, browser: { type: 'string' }, url: { type: 'string' },
  manifest: { type: 'string', default: 'docs/ui/templates.json' },
  setup: { type: 'string' }, check: { type: 'boolean' }, help: { type: 'boolean' },
} });

async function main() {
  if (args.help) {
    console.log('ui-capture --driver <package> --browser <engine> --url <app-url> [--manifest <json>] [--setup <module>] [--check]');
    return;
  }
  if (!args.driver || !args.browser || !args.url) throw Error('--driver, --browser and --url are required');
  const base = new URL(args.url);
  if (!['http:', 'https:'].includes(base.protocol)) throw Error('App URL must use http or https');
  const manifest = JSON.parse(await readFile(args.manifest, 'utf8'));
  const { viewports, templates } = manifest;
  if (!Array.isArray(templates) || !templates.length) throw Error('Manifest needs at least one template');
  for (const name of ['desktop', 'mobile']) {
    const size = viewports?.[name];
    if (!size || !['width', 'height'].every(k => Number.isInteger(size[k]) && size[k] > 0)) {
      throw Error(`Invalid ${name} viewport`);
    }
  }
  const ids = new Set();
  for (const t of templates) {
    if (typeof t.id !== 'string' || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(t.id) || ids.has(t.id)) throw Error(`Invalid or duplicate template ID: ${t.id}`);
    ids.add(t.id);
    if (typeof t.title !== 'string' || !t.title.trim() || typeof t.ready !== 'string' || !t.ready.trim()) throw Error(`${t.id}: title and ready selector required`);
    if (typeof t.path !== 'string' || !t.path.startsWith('/') || new URL(t.path, base).origin !== base.origin) throw Error(`${t.id}: path must stay on the app origin`);
  }
  const byId = new Map(templates.map(t => [t.id, t]));
  for (const t of templates) {
    const seen = new Set([t.id]);
    for (let parent = t.parent; parent != null; parent = byId.get(parent).parent) {
      if (!ids.has(parent) || seen.has(parent)) throw Error(`${t.id}: missing or cyclic parent`);
      seen.add(parent);
    }
  }
  const localRequire = createRequire(resolve('package.json'));
  const driver = await import(pathToFileURL(localRequire.resolve(args.driver)).href);
  if (!driver[args.browser]?.launch) throw Error('Configured driver does not expose the requested browser engine');
  const setup = args.setup ? await import(pathToFileURL(resolve(args.setup)).href) : {};
  const outputs = new Map();
  const browser = await driver[args.browser].launch({ headless: true });
  try {
    for (const name of ['desktop', 'mobile']) {
      const context = await browser.newContext({ viewport: viewports[name], deviceScaleFactor: 1, colorScheme: 'light', reducedMotion: 'reduce' });
      try {
        context.setDefaultTimeout(15000);
        await setup.prepare?.(context);
        for (const t of templates) {
          const page = await context.newPage();
          try {
            const response = await page.goto(new URL(t.path, base).href);
            if (!response || !response.ok()) throw Error(`${t.id}: navigation failed (${response?.status() ?? 'no response'})`);
            if (new URL(page.url()).pathname !== new URL(t.path, base).pathname) throw Error(`${t.id}: unexpected redirect to ${page.url()}`);
            await setup.ready?.(page, t);
            await page.locator(t.ready).waitFor({ state: 'visible' });
            await page.evaluate(async () => {
              const images = [...document.images].filter(img => img.getClientRects().length && getComputedStyle(img).visibility !== 'hidden');
              for (const img of images) img.loading = 'eager';
              let timer;
              try {
                await Promise.race([
                  Promise.all([document.fonts.ready, ...images.map(img => img.decode())]),
                  new Promise((_, reject) => { timer = setTimeout(() => reject(Error('Fonts or images not ready after 15 seconds')), 15000); }),
                ]);
              } finally { clearTimeout(timer); }
            });
            outputs.set(`screenshots/${t.id}/${name}.png`, await page.screenshot({ fullPage: true, animations: 'disabled', caret: 'hide' }));
          } catch (error) {
            throw Error(`${t.id}/${name}: ${error.message}`);
          } finally { await page.close(); }
        }
      } finally { await context.close(); }
    }
  } finally { await browser.close(); }

  const label = text => text.replace(/[\r\n]+/g, ' ').replace(/[\\`*_[\]<>]/g, '\\$&');
  const lines = ['# Visual sitemap', '', 'Generated from templates.json; commit this index and its screenshots with the frontend change.', ''];
  for (const name of ['desktop', 'mobile']) lines.push(`${name}: ${viewports[name].width} × ${viewports[name].height} CSS pixels; full-page captures.`);
  lines.push('');
  function tree(parent, depth) {
    for (const t of templates.filter(t => (t.parent ?? null) === parent)) {
      lines.push(`${'  '.repeat(depth)}- ${label(t.title)} (${t.id}) — route: ${label(t.path)} · [desktop](screenshots/${t.id}/desktop.png) · [mobile](screenshots/${t.id}/mobile.png)`);
      tree(t.id, depth + 1);
    }
  }
  tree(null, 0);
  outputs.set('README.md', Buffer.from(lines.join('\n') + '\n'));
  const root = dirname(resolve(args.manifest));
  const stale = [];
  for (const entry of await readdir(join(root, 'screenshots'), { withFileTypes: true }).catch(e => { if (e.code === 'ENOENT') return []; throw e; })) {
    if (!entry.isDirectory() || ids.has(entry.name)) continue;
    for (const name of ['desktop', 'mobile']) {
      const file = `screenshots/${entry.name}/${name}.png`;
      try { await readFile(join(root, file)); stale.push(file); } catch (e) { if (e.code !== 'ENOENT') throw e; }
    }
  }
  const changed = [...stale];
  for (const [file, data] of outputs) {
    let old;
    try { old = await readFile(join(root, file)); } catch (e) { if (e.code !== 'ENOENT') throw e; }
    if (!old?.equals(data)) changed.push(file);
  }
  if (args.check) {
    if (changed.length) throw Error(`Stale visual references; regenerate and review:\n${changed.join('\n')}`);
  } else {
    for (const [file, data] of outputs) {
      await mkdir(dirname(join(root, file)), { recursive: true });
      await writeFile(join(root, file), data);
    }
    for (const file of stale) await unlink(join(root, file));
  }
  console.log(`${args.check ? 'Verified' : 'Captured'} ${templates.length} templates × 2 viewports; ${changed.length} changed files.`);
}

main().catch(error => { console.error(`ui-capture: ${error.message}`); process.exitCode = 1; });
