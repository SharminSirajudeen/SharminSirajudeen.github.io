// The built page: no request leaves the site; every language renders, switches, pages and grades a quiz; no sideways
// scroll on a phone. Usage: PWCORE=<path to playwright-core> CHROME=<chrome path> node test_page.mjs
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
const { chromium } = createRequire(import.meta.url)(process.env.PWCORE);
const root = new URL('..', import.meta.url).pathname, PORT = 8765, ORIGIN = `http://127.0.0.1:${PORT}`;
const LANGS = ['en', 'hi', 'ta', 'te', 'ml'];
const data = Object.fromEntries(LANGS.map(l => [l, JSON.parse(readFileSync(new URL(`${l}.json`, import.meta.url)))]));
let n = 0, bad = 0;
const check = (ok, name) => { n++; if (!ok) bad++; console.log((ok ? 'ok   ' : 'FAIL ') + name); };

const server = spawn('python3', ['-m', 'http.server', String(PORT), '--bind', '127.0.0.1'], { cwd: root, stdio: 'ignore' });
await new Promise(r => setTimeout(r, 800));
const browser = await chromium.launch({ executablePath: process.env.CHROME });
try {
  const outside = new Set();
  const page = await browser.newPage({ viewport: { width: 375, height: 800 } });
  page.on('request', r => { if (!r.url().startsWith(ORIGIN) && !r.url().startsWith('data:')) outside.add(r.url()); });
  for (const l of LANGS) {
    const d = data[l];
    await page.goto(`${ORIGIN}/digital-marketing-course/?lang=${l}`, { waitUntil: 'networkidle' });
    check(await page.locator('h2').textContent() === d.modules[0].title, `${l}: lesson 1 title shows`);
    check(await page.evaluate(() => document.documentElement.lang) === l, `${l}: <html lang> is ${l}`);
    const q = d.modules[0].quiz[0];
    await page.locator('.q').first().locator('input').nth(q.answer).check();
    await page.locator('.q').first().locator('button').click();
    check((await page.locator('.q .fb').first().textContent()).startsWith(d.ui.correct), `${l}: the right answer is graded correct`);
    await page.locator('#next').click();
    check(await page.locator('h2').textContent() === d.modules[1].title, `${l}: Next opens lesson 2`);
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${l}: no sideways scroll at 375 px`);
  }
  await page.selectOption('#lang', 'ta');
  check(await page.locator('h2').textContent() === data.ta.modules[1].title, 'switching language keeps the lesson and changes the text');
  check(outside.size === 0, `no request leaves the site${outside.size ? ': ' + [...outside].join(', ') : ''}`);
} finally { await browser.close(); server.kill(); }
console.log(bad ? `${bad} of ${n} failed` : `page: all ${n} checks passed`);
process.exit(bad ? 1 : 0);
