import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)(process.env.PWCORE);
const b = await chromium.launch({ executablePath: process.env.CHROME });
const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
for (let i = 0; i < 4; i++) { await p.goto(`file://${process.cwd()}/slide.html?${i}#${i}`); await p.waitForTimeout(300); await p.screenshot({ path: `s${i}.png` }); }
await b.close();
