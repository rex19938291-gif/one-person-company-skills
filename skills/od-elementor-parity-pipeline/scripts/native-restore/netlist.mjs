// node netlist.mjs <網址> <mobile|desktop>：列出所有 Script 請求（網址、大小、發起者）
import { spawn, execSync } from 'node:child_process';
const [U, MODE = 'mobile'] = process.argv.slice(2); const mob = MODE === 'mobile';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const PORT = 9500 + Math.floor(Math.random() * 300), dir = `/tmp/nrnet-${PORT}`;
const ch = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [`--remote-debugging-port=${PORT}`, '--headless=new', `--user-data-dir=${dir}`, '--no-first-run', 'about:blank'], { stdio: 'ignore' });
let w; for (let i = 0; i < 50 && !w; i++) { try { w = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find((x) => x.type === 'page')?.webSocketDebuggerUrl; } catch {} await sleep(200); }
const ws = new WebSocket(w); await new Promise((r) => (ws.onopen = r)); let id = 0; const pend = new Map(); const req = {}; 
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
  if (m.method === 'Network.requestWillBeSent') { const p = m.params; req[p.requestId] = { url: p.request.url, type: p.type, init: p.initiator?.type + ' ' + (p.initiator?.url || p.initiator?.stack?.callFrames?.[0]?.url || ''), t: p.timestamp }; }
  if (m.method === 'Network.responseReceived') { const r = req[m.params.requestId]; if (r) r.type = m.params.type; }
  if (m.method === 'Network.loadingFinished') { const r = req[m.params.requestId]; if (r) r.kb = Math.round(m.params.encodedDataLength / 1024); } };
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Network.enable'); await send('Network.setCacheDisabled', { cacheDisabled: true }); await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: mob ? 390 : 1440, height: mob ? 844 : 900, deviceScaleFactor: mob ? 3 : 1, mobile: mob });
if (mob) await send('Emulation.setUserAgentOverride', { userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1' });
const t0 = Date.now() / 1000; await send('Page.navigate', { url: U }); await sleep(15000);
const list = Object.values(req).filter((r) => r.type === 'Script');
const start = Math.min(...Object.values(req).map((r) => r.t));
for (const r of list) console.log(`${String(r.kb ?? '?').padStart(4)}KB  +${(r.t - start).toFixed(1)}s  ${r.url.slice(0, 120)}  ← ${r.init.slice(0, 110)}`);
ws.close(); ch.kill('SIGKILL'); try { execSync(`rm -rf ${dir}`); } catch {} process.exit(0);
