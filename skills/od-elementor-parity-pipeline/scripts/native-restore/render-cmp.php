// ⚠ 高風險範本：會在伺服器端替指定帳號簽發 10 分鐘有效的登入憑證，用來抓「正式頁」與「草稿預覽」的渲染結果逐行比對。
// 只能在你自己有管理權、且已取得站主同意的站上執行；帳號請用專用維護帳號（不要用主要管理員）。
// 憑證在 finally 一定撤銷；執行完請確認沒有留下任何檔案或排程。不要把本檔放在網站可公開存取的目錄。
// 使用前由呼叫端把下面兩個佔位換成實際值（沒換會直接報錯，不會執行）：
//   NRPAIRS ＝ [[正式頁 ID, 草稿頁 ID], ...]
//   NRUID   ＝ 維護帳號的使用者 ID
$pairs=NRPAIRS; $uid=NRUID;
if(!is_array($pairs) || !$pairs || !is_int($uid) || $uid<1) return ['err'=>'請先填入 NRPAIRS 與 NRUID'];
$exp=time()+600;
$tok=WP_Session_Tokens::get_instance($uid)->create($exp);
$out=[];
try {
  $ck=[];
  foreach([[LOGGED_IN_COOKIE,'logged_in'],[SECURE_AUTH_COOKIE,'secure_auth'],[AUTH_COOKIE,'auth']] as $c) $ck[]=new WP_Http_Cookie(['name'=>$c[0],'value'=>wp_generate_auth_cookie($uid,$exp,$c[1],$tok)]);
  $get=function($url) use($ck){ $r=wp_remote_get($url,['cookies'=>$ck,'timeout'=>60,'sslverify'=>false]); return is_wp_error($r)?'ERR '.$r->get_error_message():wp_remote_retrieve_body($r); };
  foreach($pairs as [$a,$b]){
    $ha=$get(add_query_arg(['page_id'=>$a,'nrr'=>rand()],home_url('/')));
    $hb=$get(add_query_arg(['page_id'=>$b,'preview'=>'true','nrr'=>rand()],home_url('/')));
    foreach(['a'=>$ha,'b'=>$hb] as $k=>$h){ preg_match('#<main\b.*</main>#s',$h,$m); $out[$a][$k]=$m[0]??('NOMAIN '.substr($h,0,300)); }
  }
} finally {
  WP_Session_Tokens::get_instance($uid)->destroy($tok);
}
return $out;
