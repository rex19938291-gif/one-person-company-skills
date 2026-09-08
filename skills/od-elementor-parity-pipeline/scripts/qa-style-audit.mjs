// qa-style-audit.mjs — computed-style parity audit (visual-contract channel 2).
// Matches source↔build elements BY TEXT and diffs computed styles. Measures
// ONLY the innermost element holding the text: any element whose child carries
// the same text is a wrapper and is SKIPPED — wrapper divs inherit body font
// and produce mass false mismatches (C 客戶 2026-07-09: 205/305 phantom diffs).
//
// Hardened per skill contract C: per-URL watchdog + guaranteed tab close, so a
// heavy page can never hang the audit or leak CDP tabs. No deps, Node >= 22.
//
// Usage:
// node qa-style-audit.mjs --cdp-url http://127.0.0.1:9223 \
// --a '<source url (file:// ok)>' --b '<build url>' [--width 1440] [--max 60]
// Exit codes: 0 ok, 2 zero matched elements (invalid run), 3 watchdog timeout.
import { setTimeout as sleep } from 'node:timers/promises';

const args = process.argv.slice(2);
const getArg = (f, d = null) => { const i = args.indexOf(f); return i >= 0 ? args[i + 1] : d; };
const cdp = (getArg('--cdp-url', process.env.QA_CDP_URL || 'http://127.0.0.1:9223')).replace(/\/+$/, '');
const urlA = getArg('--a');
const urlB = getArg('--b');
const width = Number(getArg('--width', 1440));
const maxOut = Number(getArg('--max', 60));
const URL_BUDGET_MS = Number(process.env.QA_AUDIT_URL_BUDGET_MS || 150000);
if (!urlA || !urlB) { console.error('need --a <url> --b <url>'); process.exit(1); }

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

const COLLECT = `(() => {
 const norm = (s) => (s || '').replace(/\\s+/g, ' ').trim();
 const sel = 'h1,h2,h3,h4,h5,h6,p,li,a,button,.elementor-button,blockquote,.elementor-heading-title';
 const out = {};
 for (const el of document.querySelectorAll(sel)) {
 const text = norm(el.textContent);
 if (!text || text.length < 2 || text.length > 100) continue;
 let isWrapper = false;
 for (const c of el.children) { if (norm(c.textContent) === text) { isWrapper = true; break; } }
 if (isWrapper) continue;
 if (out[text]) continue;
 const cs = getComputedStyle(el);
 const rect = el.getBoundingClientRect();
 if (rect.width < 2 || rect.height < 2) continue;
 out[text] = {
 tag: el.tagName.toLowerCase(),
 ff: cs.fontFamily.replace(/["']/g, '').split(',')[0].trim().toLowerCase(),
 fs: cs.fontSize, fw: cs.fontWeight, fst: cs.fontStyle,
 lh: cs.lineHeight, ls: cs.letterSpacing,
 color: cs.color, bg: cs.backgroundColor, ta: cs.textAlign,
 };
 }
 return out;
})()`;

async function collectOnce(url) {
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
 await send('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: width < 500 });
 for (const phase of ['warmup', 'measured']) {
 await send('Page.navigate', { url });
 for (let i = 0; i < 70; i++) {
 const r = await send('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
 if (r.result.value === 'complete') break;
 await sleep(500);
 }
 if (phase === 'measured') await sleep(2000);
 }
 const r = await send('Runtime.evaluate', { expression: COLLECT, returnByValue: true });
 return r.result.value || {};
 } finally {
 try { ws && ws.close(); } catch {}
 await closeTarget(t.id);
 }
}

async function collect(url) {
 // Watchdog: a hung heavy page must fail loudly, not stall forever (contract C).
 return await Promise.race([
 collectOnce(url),
 sleep(URL_BUDGET_MS).then(() => { throw new Error(`watchdog: ${url} exceeded ${URL_BUDGET_MS}ms`); }),
 ]);
}

let A, B;
try { A = await collect(urlA); B = await collect(urlB); }
catch (e) { console.error(String(e.message || e)); process.exit(3); }

const props = [['ff', 'font'], ['fs', 'size'], ['fw', 'weight'], ['fst', 'style'], ['lh', 'lineH'], ['ls', 'letterSp'], ['color', 'color'], ['bg', 'bg'], ['ta', 'align']];
const texts = Object.keys(A);
let matched = 0, mismatchElems = 0, totalDiffs = 0;
const report = [];
for (const t of texts) {
 const a = A[t]; const b = B[t];
 if (!b) continue;
 matched++;
 const diffs = [];
 for (const [k, label] of props) if (a[k] !== b[k]) diffs.push(`${label}: src=${a[k]} | build=${b[k]}`);
 if (diffs.length) { mismatchElems++; totalDiffs += diffs.length; report.push({ t, tag: a.tag, diffs }); }
}
report.sort((x, y) => y.diffs.length - x.diffs.length);
console.log(`matched-by-text elements: ${matched} | with mismatches: ${mismatchElems} | total prop diffs: ${totalDiffs}`);
console.log(`(source-only texts: ${texts.filter((t) => !B[t]).length}, build-only: ${Object.keys(B).filter((t) => !A[t]).length})\n`);
for (const r of report.slice(0, maxOut)) {
 console.log(`[${r.tag}] "${r.t.slice(0, 60)}"`);
 for (const d of r.diffs) console.log(` - ${d}`);
}
if (matched === 0) process.exit(2);
