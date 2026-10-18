<?php
define('ABSPATH','/'); $META=[];
function add_action(){} function add_filter(){} function add_menu_page(){} function add_submenu_page(){}
function get_post_meta($id,$k){ global $META; return $META[$id]??''; } function wp_strip_all_tags($s){ return strip_tags($s); }
require __DIR__.'/zb-native.reference.php';
$ok=0;$bad=0; function t($n,$g,$e){ global $ok,$bad; if($g===$e)$ok++; else {$bad++; echo "FAIL $n: ".var_export($g,true)."\n";} }
function tog($tabs){ return ['elType'=>'widget','widgetType'=>'toggle','settings'=>['_attributes'=>"data-zbt|".base64_encode('{{@rows tabs}}<details><summary><h3>{{.tab_title}}</h3></summary><p>{{.tab_content}}</p></details>{{/rows}}'),'tabs'=>$tabs],'elements'=>[]]; }
$META[1]=json_encode([['elType'=>'container','elements'=>[tog([['tab_title'=>'問一','tab_content'=>'甲<br>乙'],['tab_title'=>'問二','tab_content'=>'<p>甲</p><p>乙</p><ul><li>丙</li><li>丁</li></ul>'],['tab_title'=>'&nbsp;','tab_content'=>'&nbsp;'],['tab_title'=>'問四','tab_content'=>'A &amp; B &lt;/script&gt;']])]]]);
$it=zb_native_faq_items(1);
t('題數（空白題略過）',count($it),3); t('換行',$it[0][1],"甲\n乙"); t('區塊不黏字',$it[1][1],"甲\n乙\n丙\n丁"); t('實體字',$it[2][1],'A & B </script>');
$META[2]=json_encode([['elType'=>'container','elements'=>[]]]); t('沒有問答元件回 null', zb_native_faq_items(2), null);
$orig=['@type'=>'FAQPage','mainEntity'=>[['x']]]; t('沒有元件沿用原資料', zb_native_faq_ld($orig,2), $orig);
$META[3]=json_encode([tog([])]); t('刪光回 null', zb_native_faq_ld($orig,3), null);
$j=json_encode(zb_native_faq_ld($orig,1),JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_HEX_TAG); t('輸出不含 </script>', strpos($j,'</script>'), false);
echo "ok=$ok bad=$bad\n";
