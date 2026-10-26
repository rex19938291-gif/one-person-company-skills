// node pubshot.mjs <網址> <輸出> <寬> <張數>：沿頁面內捲動容器逐屏截圖並接成長圖片段
import { spawn, execSync } from 'node:child_process'; import { writeFileSync } from 'node:fs';
const [U, OUT, W, N] = process.argv.slice(2); const mob = +W < 800;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const PORT = 9500 + Math.floor(Math.random() * 300), dir = `/tmp/nrps-${PORT}`;
const ch = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [`--remote-debugging-port=${PORT}`, '--headless=new', '--hide-scrollbars', `--user-data-dir=${dir}`, '--no-first-run', 'about:blank'], { stdio: 'ignore' });
let ws_; for (let i = 0; i < 50 && !ws_; i++) { try { ws_ = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find((x) => x.type === 'page')?.webSocketDebuggerUrl; } catch {} await sleep(200); }
const ws = new WebSocket(ws_); await new Promise((r) => (ws.onopen = r)); let id = 0; const pend = new Map();
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (e) => (await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true })).result?.result?.value;
await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: +W, height: mob ? 844 : 900, deviceScaleFactor: 1, mobile: mob });
if (mob) await send('Emulation.setUserAgentOverride', { userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1' });
await send('Page.navigate', { url: U }); await sleep(9000);
const H = mob ? 844 : 900;
for (let k = 0; k < +N; k++) {
  await ev(`(async()=>{const r=document.querySelector('[data-scrollroot]')||document.scrollingElement; const t=${k}*${H-60}; for(let y=r.scrollTop;y<t;y+=200){r.scrollTop=y; await new Promise(x=>setTimeout(x,60));} r.scrollTop=t; return 1})()`);
  await sleep(1800);
  const s = await send('Page.captureScreenshot', { format: 'jpeg', quality: 60 }); writeFileSync(`${OUT}-${String(k).padStart(2, '0')}.jpg`, Buffer.from(s.result.data, 'base64'));
}
ws.close(); ch.kill('SIGKILL'); try { execSync(`rm -rf ${dir}`); } catch {} process.exit(0);
