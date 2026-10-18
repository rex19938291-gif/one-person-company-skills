$pairs=[[31296,31393]];
$exp=time()+600; $uid=12;
$tok=WP_Session_Tokens::get_instance($uid)->create($exp);
$ck=[];
foreach([[LOGGED_IN_COOKIE,'logged_in'],[SECURE_AUTH_COOKIE,'secure_auth'],[AUTH_COOKIE,'auth']] as $c) $ck[]=new WP_Http_Cookie(['name'=>$c[0],'value'=>wp_generate_auth_cookie($uid,$exp,$c[1],$tok)]);
$get=function($url) use($ck){ $r=wp_remote_get($url,['cookies'=>$ck,'timeout'=>60,'sslverify'=>false]); return is_wp_error($r)?'ERR '.$r->get_error_message():wp_remote_retrieve_body($r); };
$out=[];
$dir=WP_CONTENT_DIR.'/updraft/yt-vault-20261017/native-20261017/';
foreach($pairs as [$a,$b]){
  $ha=$get(add_query_arg(['page_id'=>$a,'zbr'=>rand()],home_url('/')));
  $hb=$get(add_query_arg(['page_id'=>$b,'preview'=>'true','zbr'=>rand()],home_url('/')));
  foreach(['a'=>$ha,'b'=>$hb] as $k=>$h){ preg_match('#<main\b.*</main>#s',$h,$m); $out[$a][$k]=$m[0]??('NOMAIN '.substr($h,0,300)); }
}
WP_Session_Tokens::get_instance($uid)->destroy($tok);
return $out;
