// 將這支檔案加在已去個資的真實 WordPress 一般設定頁，不自行重畫後台。
// 頁面需保留 #blogname、#start_of_week 與 #submit；表單不會送到伺服器。
(function () {
 const $ = window.$q;
 window.PAGE = 'settings'; // 與設定檔 capture.pages 的鍵一致。
 window.addEventListener('load', () => {
 window.cleanAdmin();
 window.setScroller($('#wpcontent'));
 const setName = () => {
 $('#blogname').value = '示範商店';
 $('#start_of_week').value = '0';
 $('#blogname').focus({ preventScroll: true });
 };
 const notice = () => $('#tutorial-saved');
 const scenarios = {
 settings: {
 h: '調整一般設定', p: '確認商店名稱與一週起始日。',
 steps: [
 {
 tt: '查看設定頁', // 步驟標題，設定檔 tt 可覆寫。
 dd: '先確認目前所在頁面。', // 字卡說明，限純文字，dd 可覆寫。
 el: () => [$('#wpcontent h1'), $('#blogname')], // 函式回傳目標或陣列。
 act: () => {}, // post 狀態動作；前面的步驟會先重播。
 z: 1.6, // 原始鏡頭倍率，影片會再套用 zoom 設定。
 pad: 8, // 焦點框外擴的 CSS 像素。
 page: 'settings' // 目前步驟使用的頁面。
 },
 {
 tt: '修改商店名稱', dd: '填入示範商店，再確認一週起始日。',
 el: () => $('#blogname'), act: setName, click: true, z: 1.7,
 live: () => window.fakeList($('#start_of_week'), ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'], '星期日'),
 // live 可選：展開中示意，僅替代無法截到的原生清單，不可捏造功能。
 pre: () => { $('#blogname').value = '原始示意名稱'; }, // 目前步驟共用前置。
 view: () => {}, // 推鏡前調整視角。
 after: () => {}, // 捲動後、量座標前；寬表格可在此 translateX。
 anchor: 0.38, // 目標位於視窗高度的比例。
 spotAfter: () => $('#blogname'), // post 狀態的焦點。
 spotZ: 1.7, page: 'settings'
 // 跨頁可加 postPage；capture.phase_pages 可再覆寫頁面。
 },
 {
 tt: '確認儲存結果', dd: '按儲存後查看成功訊息。',
 el: () => $('#submit'), click: true, z: 1.6,
 act: () => {
 if (notice()) return;
 const box = document.createElement('div'); box.id = 'tutorial-saved';
 box.className = 'notice notice-success';
 box.textContent = '示意狀態：設定已儲存。';
 $('#wpcontent h1').after(box);
 }, // 只模擬已驗證過的狀態，不送出表單、不修改正式站。
 spotAfter: notice, postView: () => window.scrollTo2(0), spotZ: 1.7,
 page: 'settings'
 // scrollTo 可選：函式回傳應先捲到的元素。
 }
 ]
 }
 };
 window.runRender(scenarios);
 });
})();
