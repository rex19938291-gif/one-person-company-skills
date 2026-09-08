#!/usr/bin/env node
/**
 * OD→Elementor QA harness: section-rhythm metrics + reliable full-page screenshot
 * via Chrome CDP (no npm deps; Node >=22 for built-in WebSocket).
 *
 * Usage:
 * node qa-measure.mjs --url <URL> --width 1440 [--height 900] [--selector '.ipg-sec'] \
 * [--shot out.png] [--wait 6000] [--wait-for '.your-section-class'] [--warmup false] \
 * [--cdp-url http://127.0.0.1:9223]
 *
 * Sandboxed-executor mode: --cdp-url (or QA_CDP_URL env) connects to an
 * ALREADY-RUNNING Chrome CDP endpoint instead of spawning Chrome — for
 * executors (Codex subagents etc.) whose sandbox cannot launch processes.
 * Start the endpoint outside the sandbox with scripts/cdp-endpoint.sh.
 * In this mode we create and close only our own page target; the shared
 * browser is never killed.
 *
 * Measurement validity (model-agnostic, enforced here so executors can't skip it):
 * - warmup: by default the URL is fetched once and discarded before measuring,
 * so cold-start WP (6-11s first response) never poisons the numbers.
 * - --wait-for <selector>: after navigation, poll until document.readyState is
 * 'complete' AND the selector matches a visible element (max 30s), instead of
 * trusting a fixed --wait. Fixed waits produced 1519px-vs-10374px phantom
 * diffs on cold local WP.
 * - exit code 2 when zero blocks matched: any 0-row comparison is INVALID by
 * definition — the caller must retry, never prescribe fixes from it.
 */
import { spawn, execSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';

const args = {};
for (let i = 2; i < process.argv.length; i += 2) args[process.argv[i].replace(/^--/, '')] = process.argv[i + 1];
const URL_ = args.url;
const W = parseInt(args.width || '1440', 10);
const H = parseInt(args.height || '900', 10);
const WAIT = parseInt(args.wait || '6000', 10);
const SELECTOR = args.selector || 'header,footer,section,[data-element_type="container"].e-parent';
const PORT = 9222 + Math.floor(Math.random() * 500);
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
// Sandboxed-executor mode: connect to an existing endpoint, never spawn/kill.
const CDP_BASE = (args['cdp-url'] || process.env.QA_CDP_URL || '').replace(/\/+$/, '');
let remoteTargetId = null;

const chrome = CDP_BASE ? null : spawn(CHROME, [
 `--remote-debugging-port=${PORT}`, '--headless=new', '--disable-gpu', '--hide-scrollbars',
 `--user-data-dir=/tmp/cfab-cdp-${PORT}`, '--no-first-run', 'about:blank',
], { stdio: 'ignore' });
const cleanup = () => { if (chrome) try { chrome.kill('SIGKILL'); execSync(`rm -rf /tmp/cfab-cdp-${PORT}`); } catch {} };
process.on('exit', cleanup);
async function finish(code) {
 if (CDP_BASE && remoteTargetId) { try { await fetch(`${CDP_BASE}/json/close/${remoteTargetId}`); } catch {} }
 cleanup();
 process.exit(code);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function getWsUrl() {
 if (CDP_BASE) {
 // Shared endpoint: create our own tab (PUT for Chrome >=111, GET fallback).
 for (const method of ['PUT', 'GET']) {
 try {
 const res = await fetch(`${CDP_BASE}/json/new?about:blank`, { method });
 if (res.ok) {
 const t = await res.json();
 remoteTargetId = t.id;
 return t.webSocketDebuggerUrl;
 }
 } catch {}
 }
 throw new Error(`cannot create target at ${CDP_BASE} — is the shared endpoint running? (scripts/cdp-endpoint.sh start)`);
 }
 for (let t = 0; t < 50; t++) {
 try {
 const res = await fetch(`http://127.0.0.1:${PORT}/json/list`);
 const targets = await res.json();
 const page = targets.find((x) => x.type === 'page');
 if (page) return page.webSocketDebuggerUrl;
 } catch {}
 await sleep(200);
 }
 throw new Error('chrome CDP not reachable');
}

let msgId = 0;
const pending = new Map();
let ws;
function send(method, params = {}, sessionId) {
 const id = ++msgId;
 return new Promise((resolve, reject) => {
 pending.set(id, { resolve, reject });
 ws.send(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params }));
 });
}

// Warm-up request (discarded): local WP cold starts take 6-11s and invalidate
// timing-sensitive measurements. Disable only with --warmup false.
if (args.warmup !== 'false' && URL_) {
 try { await fetch(URL_, { signal: AbortSignal.timeout(30000) }); } catch {}
}

const wsUrl = await getWsUrl();
ws = new WebSocket(wsUrl);
await new Promise((r) => (ws.onopen = r));
ws.onmessage = (ev) => {
 const m = JSON.parse(ev.data);
 if (m.id && pending.has(m.id)) {
 const { resolve, reject } = pending.get(m.id);
 pending.delete(m.id);
 m.error ? reject(new Error(m.error.message)) : resolve(m.result);
 }
};

await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: args.mobile === 'true' });
await send('Page.enable');
await send('Page.navigate', { url: URL_ });

// Readiness wait: prefer condition-based over fixed sleep. Poll readyState
// (+ optional --wait-for selector visibility) up to 30s, then settle briefly.
{
 const waitFor = args['wait-for'];
 const cond = `(function(){
 if (document.readyState !== 'complete') return false;
 ${waitFor ? `var el=document.querySelector(${JSON.stringify(waitFor)});
 if(!el) return false;
 var r=el.getBoundingClientRect(); if(r.width<1&&r.height<1) return false;` : ''}
 return true;
 })()`;
 let ready = false;
 const deadline = Date.now() + 30000;
 while (Date.now() < deadline) {
 try {
 const r = await send('Runtime.evaluate', { expression: cond, returnByValue: true });
 if (r.result.value === true) { ready = true; break; }
 } catch {}
 await sleep(300);
 }
 if (!ready) console.error(`WARN: readiness condition not met within 30s${waitFor ? ` (--wait-for ${waitFor})` : ''}; results may be invalid`);
 await sleep(Math.min(WAIT, 3000)); // brief settle for fonts/reveal/typewriter
}

// Elementor suppresses background-image on below-fold containers until its JS
// marks them .e-lazyloaded on scroll; force-mark so full-page captures are true.
await send('Runtime.evaluate', { expression:
 `document.querySelectorAll('.e-con.e-parent').forEach(function(e){e.classList.add('e-lazyloaded');});
 document.querySelectorAll('[class*="-reveal"]').forEach(function(e){e.classList.add('in');});
 document.querySelectorAll('.tw-char').forEach(function(e){e.classList.add('show');});
 document.querySelectorAll('img[loading="lazy"]').forEach(function(i){i.loading='eager'; if(!i.complete){i.src=i.src;}});
 window.dispatchEvent(new Event('scroll'));`, returnByValue: true });
await sleep(3000);

const evalJs = async (expr) => (await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })).result.value;

if (args.eval) {
 console.log(JSON.stringify(await evalJs(args.eval), null, 1));
 if (!args.shot) await finish(0);
}

const metrics = await evalJs(`(function(){
 var sel=${JSON.stringify(SELECTOR)};
 var els=[].slice.call(document.querySelectorAll(sel)).filter(function(e){return e.offsetHeight>40 && !e.closest('[data-element_type="container"].e-parent [data-element_type="container"]') || e===e;});
 // keep only top-level blocks (direct flow children of body/main wrappers)
 var seen=[]; els.forEach(function(e){ if(!seen.some(function(s){return s.contains(e);})) seen.push(e); });
 var out=seen.map(function(e){
 var r=e.getBoundingClientRect(), y=r.top+window.scrollY;
 var id=e.id||''; var cls=(e.className&&e.className.baseVal!==undefined?'':(e.className||'')).toString().split(/\\s+/).slice(0,3).join('.');
 return {tag:e.tagName.toLowerCase(), id:id, cls:cls, top:Math.round(y), h:Math.round(r.height)};
 }).filter(function(m){return m.h>40;}).sort(function(a,b){return a.top-b.top;});
 return {pageH:Math.round(document.documentElement.scrollHeight), vw:innerWidth, blocks:out};
})()`);

console.log(JSON.stringify(metrics, null, 1));

// Zero matched blocks = invalid measurement by definition (timing flake or bad
// selector). Exit 2 so callers mechanically know to retry, not prescribe fixes.
if (!metrics || !metrics.blocks || metrics.blocks.length === 0) {
 console.error('ERROR: 0 blocks matched — measurement INVALID. Retry (check --wait-for / --selector); never prescribe fixes from this run.');
 if (!args.shot) await finish(2);
}

if (args.shot) {
 // captureBeyondViewport misses rasterizing some out-of-viewport images;
 // instead grow the emulated viewport to the full page height, let images
 // decode, then take a plain screenshot.
 const pageH = await evalJs('document.documentElement.scrollHeight');
 await send('Emulation.setDeviceMetricsOverride', { width: W, height: Math.min(pageH, 20000), deviceScaleFactor: 1, mobile: args.mobile === 'true' });
 await evalJs(`Promise.all([].slice.call(document.images).filter(i=>i.complete).map(i=>i.decode().catch(()=>{})))`);
 await sleep(2500);
 const shot = await send('Page.captureScreenshot', { format: 'png' });
 writeFileSync(args.shot, Buffer.from(shot.data, 'base64'));
 console.error(`screenshot -> ${args.shot}`);
}
await finish(0);
