import { createRequire } from 'node:module';
import http from 'node:http';
import { readFileSync, existsSync, statSync } from 'node:fs';
import { join, extname } from 'node:path';
const { chromium } = createRequire(import.meta.url)(process.env.PWCORE);
const ORIGIN = 'http://127.0.0.1:8767'; let n = 0, bad = 0;
const check = (ok, name) => { n++; if (!ok) bad++; console.log((ok ? 'ok   ' : 'FAIL ') + name); };
// a static server that answers byte ranges, as GitHub Pages does (video seeking needs them)
const TYPES = { '.html': 'text/html', '.webm': 'video/webm', '.mp4': 'video/mp4', '.woff2': 'font/woff2' };
const server = http.createServer((req, res) => {
  let f = join(process.env.ROOT, decodeURIComponent(new URL(req.url, ORIGIN).pathname));
  if (existsSync(f) && statSync(f).isDirectory()) f = join(f, 'index.html');
  if (!existsSync(f)) { res.writeHead(404).end(); return; }
  const body = readFileSync(f), m = /bytes=(\d+)-(\d*)/.exec(req.headers.range || ''), type = TYPES[extname(f)] || 'application/octet-stream';
  if (!m) { res.writeHead(200, { 'Content-Type': type, 'Accept-Ranges': 'bytes', 'Content-Length': body.length }).end(body); return; }
  const a = +m[1], b = m[2] ? +m[2] : body.length - 1;
  res.writeHead(206, { 'Content-Type': type, 'Accept-Ranges': 'bytes', 'Content-Range': `bytes ${a}-${b}/${body.length}`, 'Content-Length': b - a + 1 }).end(body.subarray(a, b + 1));
});
await new Promise(r => server.listen(8767, '127.0.0.1', r));
const b = await chromium.launch({ executablePath: process.env.CHROME });
try {
  const outside = new Set(), p = await b.newPage({ viewport: { width: 375, height: 800 } });
  p.on('request', r => { if (!r.url().startsWith(ORIGIN)) outside.add(r.url()); });
  await p.goto(ORIGIN + '/lesson-demo/', { waitUntil: 'networkidle' });
  for (const [l, label] of [['hi', 'हिन्दी'], ['ta', 'தமிழ்'], ['ml', 'മലയാളം'], ['en', 'English']]) {
    await p.evaluate(() => { document.getElementById('v').currentTime = 10; });
    await p.getByRole('button', { name: label }).click();
    const loaded = await p.waitForFunction(l => document.getElementById('v').currentSrc.endsWith(`/${l}.webm`) && document.getElementById('v').readyState >= 1, l, { timeout: 5000 }).then(() => true, () => false);
    check(loaded, `${l}: the player loads ${l}'s own file`);
    await p.waitForFunction(() => Math.abs(document.getElementById('v').currentTime - 10) < 0.5, null, { timeout: 3000 }).catch(() => {});
    const s = await p.evaluate(() => { const v = document.getElementById('v'); return { d: v.duration, t: v.currentTime }; });
    check(Math.abs(s.d - 24.68) < 0.1, `${l}: video loads from the site, ${s.d.toFixed(2)} s`);
    check(Math.abs(s.t - 10) < 0.5, `${l}: switching keeps the position (${s.t.toFixed(1)} s)`);
    check(await p.getByRole('button', { name: label }).getAttribute('aria-pressed') === 'true', `${l}: its button shows as selected`);
  }
  check(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'no sideways scroll at 375 px');
  check(outside.size === 0, 'no request leaves the site' + (outside.size ? ': ' + [...outside] : ''));
} finally { await b.close(); server.close(); }
console.log(bad ? `${bad} of ${n} failed` : `page: all ${n} checks passed`); process.exit(bad ? 1 : 0);
