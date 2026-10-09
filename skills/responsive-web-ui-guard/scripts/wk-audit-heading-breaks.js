const st=document.createElement('style');st.textContent='*{animation-duration:0s!important;transition:none!important}';document.head.appendChild(st);
await new Promise(r=>setTimeout(r,300));
const out=[];
document.querySelectorAll('h1,h2,h3,h4,.elementor-heading-title,blockquote,[class*=quote]').forEach(e=>{if(e.querySelector('h1,h2,h3'))return;const t=e.textContent.trim();if(t.length<6||t.length>80)return;const r=e.getBoundingClientRect();if(r.width<2)return;
 const rg=document.createRange();const tn=[];const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);while(w.nextNode())tn.push(w.currentNode);
 let lines=[],cur='',lastTop=null;for(const n of tn){for(let i=0;i<n.textContent.length;i++){rg.setStart(n,i);rg.setEnd(n,i+1);const rr=rg.getClientRects()[0];if(!rr){cur+=n.textContent[i];continue}const fs=parseFloat(getComputedStyle(e).fontSize);const top=(rr.top+rr.bottom)/2;if(lastTop!==null&&top>lastTop+fs*0.6){lines.push(cur);cur=''}lastTop=top;cur+=n.textContent[i]}}lines.push(cur);
 if(lines.length>1)out.push(lines.map(s=>s.trim()).join(' ｜ '))});
return JSON.stringify([...new Set(out)]);
