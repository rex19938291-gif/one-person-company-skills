// Node.js 22.4+（內建 WebSocket）。只將經使用者核准的旁白文字傳給 Google。
// node tts_gemini_live.mjs lines.json outdir [model] [voice]
import {readFileSync, writeFileSync, mkdirSync, existsSync} from 'node:fs';
import {join} from 'node:path';
const [linesFile, outDir, modelArg, voiceArg] = process.argv.slice(2);
if (!linesFile || !outDir) { console.error('用法：tts_gemini_live.mjs lines.json outdir [model] [voice]'); process.exit(1); }
const MODEL = modelArg || process.env.VO_MODEL || 'models/gemini-3.8-live';
const VOICE = voiceArg || process.env.VO_VOICE || 'Achernar';
const key = process.env.GEMINI_API_KEY;
if (!key) { console.error('缺少 GEMINI_API_KEY'); process.exit(1); }
const lines = JSON.parse(readFileSync(linesFile, 'utf8'));
const seen = new Set();
for (const row of lines) {
  if (!/^[A-Za-z0-9_-]+$/.test(row.id) || seen.has(row.id) || typeof row.text !== 'string' || !row.text.trim()) throw new Error('句子識別或文字不正確');
  seen.add(row.id);
}
mkdirSync(outDir, {recursive:true});
const file = join(outDir,'transcripts.json');
const transcripts = existsSync(file) ? JSON.parse(readFileSync(file,'utf8')) : {};
const count = text => Array.from(text.replace(/[\p{P}\p{S}\s]/gu,'')).length;
const plausible = (text,sec) => Number.isFinite(sec) && sec>0 && count(text)/sec>=2.2 && count(text)/sec<=7;
const SYS='你是台灣教學影片旁白員，請自然、清楚、稍慢地逐字朗讀使用者提供的文字。不得增加、刪減、改寫、問候或回應內容，不念任何額外說明。';
function wav(pcm, rate) {
  const h=Buffer.alloc(44);h.write('RIFF');h.writeUInt32LE(36+pcm.length,4);h.write('WAVE',8);h.write('fmt ',12);
  h.writeUInt32LE(16,16);h.writeUInt16LE(1,20);h.writeUInt16LE(1,22);h.writeUInt32LE(rate,24);h.writeUInt32LE(rate*2,28);
  h.writeUInt16LE(2,32);h.writeUInt16LE(16,34);h.write('data',36);h.writeUInt32LE(pcm.length,40);return Buffer.concat([h,pcm]);
}
function speak(text) {
  return new Promise((resolve,reject)=>{
    // 不輸出網址、金鑰或服務原始錯誤訊息。
    const ws=new WebSocket('wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key='+encodeURIComponent(key));
    let done=false,said='',rate=24000;const chunks=[];
    const finish=(error,result)=>{if(done)return;done=true;clearTimeout(timer);ws.close();error?reject(new Error(error)):resolve(result);};
    const timer=setTimeout(()=>finish('錄音等待時間過長'),60000);
    ws.onopen=()=>ws.send(JSON.stringify({setup:{model:MODEL,generationConfig:{responseModalities:['AUDIO'],speechConfig:{voiceConfig:{prebuiltVoiceConfig:{voiceName:VOICE}}}},systemInstruction:{parts:[{text:SYS}]},outputAudioTranscription:{}}}));
    // 串行處理 Blob，避免 turnComplete 早於音訊解碼完成。
    let queue=Promise.resolve();
    ws.onmessage=ev=>{queue=queue.then(async()=>{
      if(done)return;
      const raw=typeof ev.data==='string'?ev.data:Buffer.from(await ev.data.arrayBuffer()).toString('utf8');
      const m=JSON.parse(raw);if(m.error){finish('服務拒絕錄音，請檢查模型、音色與權限');return;}
      if(m.setupComplete){ws.send(JSON.stringify({clientContent:{turns:[{role:'user',parts:[{text:'請逐字念：'+text}]}],turnComplete:true}}));return;}
      const sc=m.serverContent;if(!sc)return;
      for(const p of sc.modelTurn?.parts||[])if(p.inlineData?.data){
        const mime=p.inlineData.mimeType||'';if(!mime.startsWith('audio/pcm')){finish('音訊格式不支援');return;}
        const r=Number(/rate=(\d+)/.exec(mime)?.[1]||24000);if(chunks.length&&r!==rate){finish('音訊取樣率改變');return;}rate=r;chunks.push(Buffer.from(p.inlineData.data,'base64'));
      }
      if(sc.outputTranscription?.text)said+=sc.outputTranscription.text;
      if(sc.interrupted){finish('錄音被中斷');return;}
      if(sc.turnComplete)finish(null,{pcm:Buffer.concat(chunks),said,rate});
    }).catch(()=>finish('錄音資料解析失敗'));};
    ws.onerror=()=>finish('錄音連線失敗');ws.onclose=()=>finish('錄音連線提前結束');
  });
}
for(const {id,text} of lines){
  const output=join(outDir,id+'.wav'),old=transcripts[id];
  if(existsSync(output)&&old?.text===text&&old.model===MODEL&&old.voice===VOICE&&plausible(text,old.sec))continue;
  let success=false;
  for(let attempt=1;attempt<=2;attempt++){
    try{
      const {pcm,said,rate}=await speak(text),sec=pcm.length/(rate*2);
      if(pcm.length<2||pcm.length%2||!plausible(text,sec))throw new Error('字數與秒數不符，可能截斷');
      writeFileSync(output,wav(pcm,rate));
      transcripts[id]={text,said,sec:Number(sec.toFixed(3)),model:MODEL,voice:VOICE,review:'待人工聽驗；轉寫不一定回傳'};
      success=true;break;
    }catch{console.error(id,'第'+attempt+'次錄音未通過');}
  }
  writeFileSync(file,JSON.stringify(transcripts,null,2)+'\n');
  if(!success){console.error(id,'連續兩次失敗，停止；未完成句子不可交付');process.exit(1);}
  console.log(id,transcripts[id].sec+' 秒');
}
