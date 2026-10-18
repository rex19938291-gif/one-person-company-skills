// 用法：node edshot.mjs <網址> <輸出前綴> <寬> <cookie檔> [等待秒] [執行的 JS 檔]
import { spawn, execSync } from 'node:child_process';
import { writeFileSync, readFileSync } from 'node:fs';
const [URL_, OUT, W = '1440', CK, WAIT = '25', JSF] = process.argv.slice(2);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const PORT = 9500 + Math.floor(Math.random() * 300), dir = `/tmp/zbed-${PORT}`;
const ch = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [`--remote-debugging-port=${PORT}`, '--headless=new', '--hide-scrollbars', `--user-data-dir=${dir}`, '--no-first-run', 'about:blank'], { stdio: 'ignore' });
let wsUrl; for (let i = 0; i < 50 && !wsUrl; i++) { try { wsUrl = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find((x) => x.type === 'page')?.webSocketDebuggerUrl; } catch {} await sleep(200); }
const ws = new WebSocket(wsUrl); await new Promise((r) => (ws.onopen = r));
let id = 0; const pend = new Map(); const logs = [];
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } if (m.method === 'Runtime.exceptionThrown') logs.push('EXC ' + (m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text).slice(0, 200)); if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') logs.push('ERR ' + JSON.stringify(m.params.args.map(a => a.value || a.description)).slice(0, 200)); };
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (e) => { const r = await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true }); return r.result?.result?.value ?? r.result?.exceptionDetails?.exception?.description; };
await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
for (const c of JSON.parse(readFileSync(CK, 'utf8')).c) await send('Network.setCookie', { name: c.name, value: c.value, domain: new URL(URL_).hostname, path: '/', secure: true, httpOnly: true });
await send('Emulation.setDeviceMetricsOverride', { width: +W, height: 900, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: URL_ });
await sleep(+WAIT * 1000);
if (JSF) { const r = await ev(readFileSync(JSF, 'utf8')); console.log('JS:', typeof r === 'string' ? r.slice(0, 3000) : JSON.stringify(r).slice(0, 3000)); await sleep(4000); }
if (process.env.STEPS) {
  const ed = URL_.includes('action=elementor');
  if (ed) { await ev("try{$e.run('navigator/close')}catch(e){}; 1"); await sleep(800); }
  const H = +(await ev(ed ? "document.getElementById('elementor-preview-iframe').contentDocument.documentElement.scrollHeight" : "document.documentElement.scrollHeight"));
  const box = ed ? await ev("(()=>{const r=document.getElementById('elementor-preview-iframe').getBoundingClientRect();return [r.x,r.y,r.width,r.height]})()") : [0,0,+W,900];
  console.log('H', H, 'box', JSON.stringify(box));
  for (let y = 0, k = 0; y < H && k < +process.env.STEPS; y += box[3] - 40, k++) {
    await ev(ed ? `document.getElementById('elementor-preview-iframe').contentWindow.scrollTo(0,${y});1` : `window.scrollTo(0,${y});1`);
    await sleep(1500);
    const s2 = await send('Page.captureScreenshot', { format: 'jpeg', quality: 70, clip: { x: box[0], y: box[1], width: box[2], height: box[3], scale: 0.6 } });
    writeFileSync(`${OUT}-${String(k).padStart(2,'0')}.jpg`, Buffer.from(s2.result.data, 'base64'));
  }
} else {
const shot = await send('Page.captureScreenshot', { format: 'jpeg', quality: 72 });
writeFileSync(`${OUT}.jpg`, Buffer.from(shot.result.data, 'base64'));
}
console.log('logs', JSON.stringify(logs.slice(0, 15)));
ws.close(); ch.kill('SIGKILL'); try { execSync(`rm -rf ${dir}`); } catch {}
process.exit(0);
