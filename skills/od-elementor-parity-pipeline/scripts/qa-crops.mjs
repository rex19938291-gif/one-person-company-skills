// qa-crops.mjs — targeted viewport crops for PM visual review (visual-contract
// channel 3, review loop). For each --find "text" anchor: scrollIntoView, then
// a plain viewport Page.captureScreenshot — deliberately NOT
// captureBeyondViewport, which hangs on wide/heavy pages; viewport shots are
// fast and never stall. The PM must READ the produced crops (contract B3).
// No deps, Node >= 22.
//
// Usage:
// node qa-crops.mjs --cdp-url http://127.0.0.1:9223 --url '<page url>' \
// --out <dir> [--width 1440] --find "文字錨點1" --find "文字錨點2" ...
import { setTimeout as sleep } from 'node:timers/promises';
import { writeFileSync, mkdirSync } from 'node:fs';

const args = process.argv.slice(2);
const getArg = (f, d = null) => { const i = args.indexOf(f); return i >= 0 ? args[i + 1] : d; };
const finds = []; for (let i = 0; i < args.length; i++) if (args[i] === '--find' && args[i + 1]) finds.push(args[i + 1]);
const cdp = (getArg('--cdp-url', process.env.QA_CDP_URL || 'http://127.0.0.1:9223')).replace(/\/+$/, '');
const url = getArg('--url');
const out = getArg('--out', '/tmp/qa-crops');
const width = Number(getArg('--width', 1440));
const BUDGET_MS = Number(process.env.QA_CROPS_BUDGET_MS || 180000);
if (!url || !finds.length) { console.error('need --url <page> and at least one --find "text"'); process.exit(1); }
mkdirSync(out, { recursive: true });

async function newTarget() {
 for (const method of ['PUT', 'GET']) {
 try { const r = await fetch(`${cdp}/json/new?about:blank`, { method }); if (r.ok) return await r.json(); } catch {}
 }
 throw new Error('cannot create CDP target at ' + cdp);
}
const closeTarget = async (id) => { try { await fetch(`${cdp}/json/close/${id}`); } catch {} };
function makeCdp(ws) {
 let id = 0; const pending = new Map();
 ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
 return (method, params = {}) => new Promise((res, rej) => {
 const mid = ++id; pending.set(mid, (m) => m.error ? rej(new Error(m.error.message)) : res(m.result));
 ws.send(JSON.stringify({ id: mid, method, params }));
 });
}

async function run() {
 const t = await newTarget();
 let ws;
 try {
 ws = new WebSocket(t.webSocketDebuggerUrl);
 await Promise.race([
 new Promise((r) => { ws.onopen = r; }),
 sleep(10000).then(() => { throw new Error('ws open timeout'); }),
 ]);
 const send = makeCdp(ws);
 await send('Page.enable'); await send('Runtime.enable');
 await send('Emulation.setDeviceMetricsOverride', { width, height: width < 500 ? 844 : 900, deviceScaleFactor: 1, mobile: width < 500 });
 for (const phase of ['warmup', 'measured']) { // cold local WP returns partial renders
 await send('Page.navigate', { url });
 for (let i = 0; i < 70; i++) {
 const r = await send('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
 if (r.result.value === 'complete') break;
 await sleep(500);
 }
 }
 // trigger lazyload once
 await send('Runtime.evaluate', { expression: 'window.scrollTo(0,document.body.scrollHeight)' }); await sleep(1200);
 await send('Runtime.evaluate', { expression: 'window.scrollTo(0,0)' }); await sleep(600);
 let n = 0;
 for (const text of finds) {
 n++;
 const found = await send('Runtime.evaluate', { returnByValue: true, expression: `(()=>{
 const norm=(s)=>(s||'').replace(/\\s+/g,' ').trim();
 const el=[...document.querySelectorAll('h1,h2,h3,p,li,a,button,div,section')]
 .find(e=>norm(e.textContent).startsWith(${JSON.stringify(text)})&&e.getBoundingClientRect().height>2);
 if(!el) return false;
 el.scrollIntoView({block:'center'});
 return true;
 })()` });
 await sleep(900);
 const slug = String(n).padStart(2, '0') + '-' + text.replace(/[^\p{L}\p{N}]+/gu, '').slice(0, 12);
 if (!found.result.value) { console.log(`MISS ${slug} (anchor text not found)`); continue; }
 const s = await Promise.race([
 send('Page.captureScreenshot', { format: 'png' }),
 sleep(20000).then(() => null),
 ]);
 if (s?.data) { writeFileSync(`${out}/${slug}.png`, Buffer.from(s.data, 'base64')); console.log(`shot ${out}/${slug}.png`); }
 else console.log(`FAIL ${slug} (capture timeout)`);
 }
 } finally {
 try { ws && ws.close(); } catch {}
 await closeTarget(t.id);
 }
}

try {
 await Promise.race([
 run(),
 sleep(BUDGET_MS).then(() => { throw new Error(`watchdog: exceeded ${BUDGET_MS}ms`); }),
 ]);
} catch (e) { console.error(String(e.message || e)); process.exit(3); }
