// Playwright smoke test for the Game Center (Node >= 18, only dependency: playwright).
// Usage: node tests/smoke.mjs [--only "Name"] [--out test-results]
// Exit code 0 = all games pass, 1 = at least one failure. Writes report.json + screenshots.
import { createRequire } from 'node:module';
import { spawn, execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { readdirSync, statSync, mkdirSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, relative, sep, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import net from 'node:net';

const { chromium } = createRequire(import.meta.url)('playwright');

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const arg = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const OUT = join(ROOT, arg('--out', 'test-results'));
const ONLY = arg('--only', null);
const SKIP_DIRS = new Set(['node_modules', 'scripts', '_site', 'tests', 'test-results', 'docs']);

// Same discovery rules as scripts/build_catalog.py
function findGames(dir) {
  const games = [];
  for (const name of readdirSync(dir)) {
    if (name.startsWith('.') || SKIP_DIRS.has(name)) continue;
    const full = join(dir, name);
    if (statSync(full).isDirectory()) games.push(...findGames(full));
    else if (/\.html?$/i.test(name) && full !== join(ROOT, 'index.html')) games.push(full);
  }
  return games;
}

const freePort = () => new Promise(res => { const s = net.createServer().listen(0, () => { const p = s.address().port; s.close(() => res(p)); }); });

async function startServer() {
  const port = await freePort();
  const proc = spawn('python3', ['-m', 'http.server', String(port), '--bind', '127.0.0.1'], { cwd: ROOT, stdio: 'ignore' });
  for (let i = 0; i < 50; i++) {
    try { await (await fetch(`http://127.0.0.1:${port}/index.html`)).arrayBuffer(); return { proc, base: `http://127.0.0.1:${port}/` }; }
    catch { await new Promise(r => setTimeout(r, 100)); }
  }
  proc.kill(); throw new Error('static server did not start');
}

// External (CDN) requests are fetched once with curl and served from a local cache:
// deterministic runs, works behind proxies, and records every external dependency.
const CACHE = join(OUT, '.cdn-cache');
const externalDeps = new Set();
async function routeExternal(page, base) {
  await page.route(url => !url.href.startsWith(base) && /^https?:/.test(url.href), async route => {
    const url = route.request().url();
    externalDeps.add(url);
    const file = join(CACHE, createHash('sha256').update(url).digest('hex'));
    try {
      if (!existsSync(file)) { mkdirSync(CACHE, { recursive: true }); await promisify(execFile)('curl', ['-sSfL', '--max-time', '30', '-o', file, url]); }
      const type = /\.css(\?|$)/.test(url) ? 'text/css' : /\.m?js(\?|$)/.test(url) ? 'text/javascript' : undefined;
      await route.fulfill({ body: readFileSync(file), contentType: type });
    } catch { await route.abort(); }
  });
}

const urlFor = (base, file) => base + relative(ROOT, file).split(sep).map(encodeURIComponent).join('/');
const slug = file => relative(ROOT, file).replace(/[^\p{L}\p{N}]+/gu, '_');

async function testGame(browser, base, file) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const errors = [], warnings = [];
  page.on('pageerror', e => errors.push(`uncaught: ${e.message}`));
  page.on('console', m => { if (m.type() === 'error') warnings.push(`console: ${m.text()}`); });
  page.on('requestfailed', r => { if (!r.url().startsWith('data:')) warnings.push(`request failed: ${r.url()}`); });
  const result = { game: relative(ROOT, file), ok: false, errors, warnings };
  await routeExternal(page, base);
  try {
    const resp = await page.goto(urlFor(base, file), { waitUntil: 'load', timeout: 30000 });
    if (!resp || !resp.ok()) errors.push(`HTTP ${resp?.status()}`);
    await page.waitForTimeout(1000);
    const visual = await page.evaluate(() => ({
      canvas: document.querySelectorAll('canvas').length,
      textLength: document.body?.innerText.trim().length ?? 0,
      title: document.title,
    }));
    if (!visual.canvas && visual.textLength === 0) errors.push('page renders nothing (no canvas, no text)');
    // Simulate a player: click, start keys, movement keys
    await page.mouse.click(640, 360);
    for (const key of ['Enter', 'Space', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'KeyW', 'KeyA', 'KeyS', 'KeyD']) {
      await page.keyboard.down(key); await page.waitForTimeout(60); await page.keyboard.up(key);
    }
    await page.waitForTimeout(1500);
    await page.screenshot({ path: join(OUT, `${slug(file)}.png`) });
    Object.assign(result, visual);
    result.ok = errors.length === 0;
  } catch (e) {
    errors.push(`exception: ${e.message.split('\n')[0]}`);
  }
  await page.close();
  return result;
}

async function testIndex(browser, base, games) {
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(`uncaught: ${e.message}`));
  await page.goto(base + 'index.html');
  const links = await page.$$eval('a.game', as => as.map(a => a.href));
  if (links.length !== games.length) errors.push(`catalog lists ${links.length} games, repo has ${games.length}`);
  for (const href of links) {
    const r = await fetch(href); await r.arrayBuffer();
    if (!r.ok) errors.push(`broken card link ${href} -> ${r.status}`);
  }
  await page.fill('#search', 'zzzz-kein-treffer');
  if (!(await page.isVisible('#empty'))) errors.push('search: empty state not shown');
  await page.fill('#search', '');
  await page.close();
  return { game: 'index.html', ok: errors.length === 0, errors, warnings: [] };
}

mkdirSync(OUT, { recursive: true });
let games = findGames(ROOT).sort();
if (ONLY) games = games.filter(g => relative(ROOT, g).includes(ONLY));
const { proc, base } = await startServer();
const browser = await chromium.launch();
const results = [];
try {
  if (!ONLY) results.push(await testIndex(browser, base, games));
  for (const g of games) results.push(await testGame(browser, base, g));
} finally {
  await browser.close(); proc.kill();
}
for (const r of results) {
  console.log(`${r.ok ? 'PASS' : 'FAIL'}  ${r.game}`);
  for (const e of r.errors) console.log(`      ✗ ${e}`);
  for (const w of r.warnings) console.log(`      ! ${w}`);
}
const failed = results.filter(r => !r.ok).length;
if (externalDeps.size) console.log(`\nExternal runtime dependencies:\n  ${[...externalDeps].sort().join('\n  ')}`);
writeFileSync(join(OUT, 'report.json'), JSON.stringify({ passed: results.length - failed, failed, externalDeps: [...externalDeps].sort(), results }, null, 2));
console.log(`\n${results.length - failed}/${results.length} passed — report: ${relative(ROOT, OUT)}/report.json`);
process.exit(failed ? 1 : 0);
