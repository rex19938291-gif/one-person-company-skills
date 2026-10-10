// 本機去個資後台頁的拍攝輔助；先設定 window.TUTORIAL_CONFIG。
(function () {
 const $ = s => document.querySelector(s);
 const $$ = s => [...document.querySelectorAll(s)];
 window.$q = $;
 window.$$q = $$;
 function error(message) {
 const node = document.createElement('pre');
 node.textContent = '@@ERR ' + message + '@@';
 document.documentElement.append(node);
 }
 window.addEventListener('error', e => error(e.message));
 const config = () => window.TUTORIAL_CONFIG || {};
 const height = () => config().capture?.height || 860;
 window.cleanAdmin = function (options = config().cleanup || {}) {
 // 移除整個元素；不得在 HTML 字串上刪掉工具名稱。
 for (const selector of options.removeSelectors || []) $$(selector).forEach(e => e.remove());
 for (const selector of options.hideSelectors || []) $$(selector).forEach(e => { e.style.display = 'none'; });
 for (const entry of options.textReplacements || []) $$(entry.selector).forEach(e => { e.textContent = entry.value; });
 for (const selector of options.clearSelectors || []) $$(selector).forEach(e => {
 e.value = ''; e.removeAttribute('value'); e.textContent = '';
 });
 $$('script:not([data-tutorial-runtime]), input[name*="nonce"], input[type="password"]').forEach(e => e.remove());
 $$('*').forEach(e => [...e.attributes].forEach(a => {
 if (/^on/i.test(a.name) || /nonce/i.test(a.name)) e.removeAttribute(a.name);
 }));
 $$('form').forEach(e => e.addEventListener('submit', event => event.preventDefault()));
 const bar = $('#wpadminbar');
 if (bar && bar.parentElement !== document.body) document.body.append(bar);
 if (!$('#tutorial-capture-style')) {
 const style = document.createElement('style');
 style.id = 'tutorial-capture-style';
 style.textContent = 'html,body{overflow:hidden!important}.tutorial-dd{position:fixed;z-index:999999;background:white;border:1px solid #888;box-shadow:0 6px 18px #0003;font:14px/1.4 sans-serif;color:#222;padding:4px 0;border-radius:4px}.tutorial-dd div{padding:7px 12px;white-space:nowrap}.tutorial-dd .on{background:#2271b1;color:white}';
 document.head.append(style);
 }
 };
 let scroller = null, originalTransform = '';
 window.scrollY0 = 0;
 window.setScroller = function (element) {
 if (!element) throw new Error('找不到捲動容器');
 scroller = element;
 originalTransform = element.style.transform;
 window.scrollY0 = 0;
 };
 window.scrollTo2 = function (value) {
 if (!scroller) return;
 scroller.style.transform = originalTransform;
 // 每次重新量測，避免新增列後仍沿用舊高度。
 const bottom = Math.max(height(), ...[scroller, ...scroller.querySelectorAll(config().scrollSelectors || 'table,form,section,div,ul')]
 .map(e => e.getBoundingClientRect().bottom));
 const y = Math.min(Math.max(0, Math.round(value)), Math.max(0, bottom - height() + 24));
 scroller.style.transform = `${originalTransform} translateY(-${y}px)`;
 window.scrollY0 = y;
 if (window.afterScroll) window.afterScroll();
 };
 window.ensureVisible = function (elements, anchor = 0.38) {
 elements = [].concat(elements).filter(Boolean);
 if (!elements.length) throw new Error('找不到焦點元素');
 window.scrollTo2(0);
 const rects = elements.map(e => e.getBoundingClientRect());
 const top = Math.min(...rects.map(r => r.top)), bottom = Math.max(...rects.map(r => r.bottom));
 let y = 0;
 if (bottom > height() - 40 || top < 60) {
 y = top - height() * anchor;
 if (bottom - y > height() - 40) y = bottom - height() + 60;
 }
 window.scrollTo2(y);
 };
 window.rectOfEls = function (elements, pad = 0) {
 elements = [].concat(elements).filter(Boolean);
 if (!elements.length) throw new Error('找不到座標目標');
 const rects = elements.map(e => e.getBoundingClientRect());
 const x = Math.min(...rects.map(r => r.left)) - pad, y = Math.min(...rects.map(r => r.top)) - pad;
 const right = Math.max(...rects.map(r => r.right)) + pad, bottom = Math.max(...rects.map(r => r.bottom)) + pad;
 return { x, y, w: right - x, h: bottom - y };
 };
 window.fakeList = function (anchor, list, selected, options = {}) {
 if (!anchor) throw new Error('找不到下拉選單');
 $$('.tutorial-dd').forEach(e => e.remove());
 const rect = anchor.getBoundingClientRect(), node = document.createElement('div');
 node.className = 'tutorial-dd' + (options.cls ? ' ' + options.cls : '');
 node.style.left = rect.left + 'px'; node.style.top = rect.bottom + 2 + 'px';
 node.style.minWidth = rect.width + 'px';
 list.forEach(text => {
 const row = document.createElement('div'); row.textContent = text;
 if (text === selected) row.className = 'on'; node.append(row);
 });
 document.body.append(node);
 return node;
 };
 window.runRender = function (scenarios, base = () => {}) {
 try {
 const [key, rawIndex, phase] = decodeURIComponent(location.hash.slice(3)).split(',');
 const scenario = scenarios[key], index = Number(rawIndex), step = scenario?.steps[index];
 if (!location.hash.startsWith('#r=') || !step || !Number.isInteger(index) || !['pre', 'mid', 'post'].includes(phase)) throw new Error('無效情境、步數或拍攝階段');
 const page = (phase === 'post' && step.postPage) || step.page;
 if (page && window.PAGE && page !== window.PAGE) throw new Error('步驟與頁面不符');
 base(key);
 // 跨頁步驟只重播目前頁面的動作，避免存取另一頁不存在的元素。
 for (let i = 0; i < index; i++) {
 const previous = scenario.steps[i];
 if (!previous.page || !window.PAGE || previous.page === window.PAGE) previous.act?.(false);
 }
 step.pre?.();
 const target = () => [].concat(typeof step.el === 'function' ? step.el() : step.el);
 const after = () => step.spotAfter ? [].concat(typeof step.spotAfter === 'function' ? step.spotAfter() : step.spotAfter) : target();
 if (phase === 'post') {
 step.act?.(true);
 if (step.postView) step.postView();
 else { step.view?.(); window.ensureVisible(step.scrollTo ? step.scrollTo() : after(), step.anchor); }
 } else {
 step.view?.(); window.ensureVisible(step.scrollTo ? step.scrollTo() : target(), step.anchor);
 }
 // 包含 postView 的 post 也要執行，且一定在量座標前。
 step.after?.();
 const rect = window.rectOfEls(phase === 'post' ? after() : target(), step.pad);
 if (phase === 'mid') { if (!step.live) throw new Error('沒有展開中動作'); step.live(); }
 $('#out')?.remove();
 const node = document.createElement('pre'); node.id = 'out'; node.style.display = 'none';
 node.textContent = '@@' + JSON.stringify({ sy: window.scrollY0, r: rect, n: scenario.steps.length, h: scenario.h, p: scenario.p,
 page: page || window.PAGE, meta: scenario.steps.map(s => ({ tt: s.tt, dd: s.dd, click: !!s.click, z: s.z || 1.6,
 spotZ: s.spotZ || null, live: !!s.live, page: s.page || null, postPage: s.postPage || null })) }) + '@@';
 document.body.append(node);
 } catch (err) { error(err.message); }
 };
})();
