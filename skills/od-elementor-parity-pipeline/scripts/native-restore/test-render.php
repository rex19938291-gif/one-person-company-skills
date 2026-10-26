<?php
define('ABSPATH','/');
function add_action(){} function add_filter(){} function add_menu_page(){} function add_submenu_page(){} function esc_attr($s){return htmlspecialchars((string)$s,ENT_QUOTES);} function esc_url_raw($u){return preg_match('#^(https?:|tel:|mailto:|/|\#)#i',$u)?$u:'';}
function wp_get_attachment_image_url($id){return $id==9?'/new.webp':'';} function wp_get_attachment_image_srcset($id){return $id==9?'/new-480.webp 480w, /new.webp 1200w':'';}
function get_post_meta($id){return $id==9?'新圖 $1 ${1} 說明':'';}
require __DIR__.'/nr-native.reference.php';
class E{ public $s,$n; function __construct($n,$s){$this->n=$n;$this->s=$s;} function get_settings($k){return $this->s[$k]??'';} function get_settings_for_display(){return $this->s;} function get_name(){return $this->n;} function get_type(){return 'widget';} }
function mk($n,$s,$tpl,$extra=''){ $s['_attributes']="data-nrt|".base64_encode($tpl).($extra?"\n".$extra:''); $s['_css_classes']='nr-n'; return new E($n,$s); }
$ok=0;$bad=0; function t($name,$got,$exp){ global $ok,$bad; if($got===$exp){$ok++;} else {$bad++; echo "FAIL $name\n  got: $got\n  exp: $exp\n";} }
// 富文字
$tp='<p style="c">{{editor}}</p>';
t('一段', nr_native_render(mk('text-editor',['editor'=>'甲<a href="/x">連</a>'],$tp)), '<p style="c">甲<a href="/x">連</a></p>');
t('包p', nr_native_render(mk('text-editor',['editor'=>'<p>甲</p>'],$tp)), '<p style="c">甲</p>');
t('兩段', nr_native_render(mk('text-editor',['editor'=>"<p>甲</p>\n<p>乙</p>"],$tp)), '<p style="c">甲</p><p style="c">乙</p>');
t('段+清單', nr_native_render(mk('text-editor',['editor'=>'<p>甲</p><ul><li>乙</li></ul>'],$tp)), '<p style="c">甲</p><ul><li>乙</li></ul>');
t('對齊段', nr_native_render(mk('text-editor',['editor'=>'<p style="text-align:center">甲</p><p>乙</p>'],$tp)), '<p style="c">甲</p><p style="c">乙</p>');
t('裸字+清單', nr_native_render(mk('text-editor',['editor'=>"甲\n<ul><li>乙</li></ul>"],$tp)), '<p style="c">甲</p><ul><li>乙</li></ul>');
// 逐列
$rt='<dl s>{{@rows tabs}}<div r><dt d>{{.tab_title}}</dt><dd e>{{.tab_content}}</dd></div>{{/rows}}</dl>';
$rows=[['_id'=>'a','tab_title'=>'地址','tab_content'=>'X'],['_id'=>'b','tab_title'=>'電話','tab_content'=>'Y'],['_id'=>'c','tab_title'=>'新','tab_content'=>'Z']];
t('列三筆', nr_native_render(mk('toggle',['tabs'=>$rows],$rt)), '<dl s><div r><dt d>地址</dt><dd e>X</dd></div><div r><dt d>電話</dt><dd e>Y</dd></div><div r><dt d>新</dt><dd e>Z</dd></div></dl>');
t('列交換刪', nr_native_render(mk('toggle',['tabs'=>[$rows[1]]],$rt)), '<dl s><div r><dt d>電話</dt><dd e>Y</dd></div></dl>');
$ft='<details s><summary u><h3 h>{{@rows tabs}}{{.tab_title}}</h3></summary><p p>{{.tab_content}}</p>{{/rows}}</details>';
$ct='<ol o>{{@rows icon_list}}<li l><span a>{{.#zh}}</span><span b>{{.text}}</span></li>{{/rows}}</ol>';
t('中文序號', nr_native_render(mk('icon-list',['icon_list'=>[['text'=>'手卷'],['text'=>'前菜']]],$ct)), '<ol o><li l><span a>一</span><span b>手卷</span></li><li l><span a>二</span><span b>前菜</span></li></ol>');
// 連結
$bt='<a href="{{link}}" c>{{text}}</a>';
t('連結', nr_native_render(mk('button',['text'=>'訂','link'=>['url'=>'https://a.b/?x=1&y=2']],$bt)), '<a href="https://a.b/?x=1&amp;y=2" c>訂</a>');
t('危險連結', nr_native_render(mk('button',['text'=>'訂','link'=>['url'=>'javascript:alert(1)']],$bt)), '<a href="" c>訂</a>');
// 照片
$it='<img src="/old.webp" srcset="/old-480.webp 480w" sizes="100vw" alt="舊" style="s">';
t('未換', nr_native_render(mk('image',['image'=>['id'=>5,'url'=>'/old.webp']],$it,'data-nri|5')), $it);
t('換圖$1', nr_native_render(mk('image',['image'=>['id'=>9,'url'=>'/new.webp']],$it,'data-nri|5')), '<img srcset="/new-480.webp 480w, /new.webp 1200w" src="/new.webp" sizes="100vw" alt="新圖 $1 ${1} 說明" style="s">');
t('清除', nr_native_render(mk('image',['image'=>['id'=>0,'url'=>'']],'<div>'.$it.'</div>','data-nri|5')), '<div></div>');
t('外部網址', nr_native_render(mk('image',['image'=>['id'=>0,'url'=>'https://x.y/p.jpg','alt'=>'外']],$it,'data-nri|5')), '<img src="https://x.y/p.jpg" sizes="100vw" alt="外" style="s">');
$lz='<img src="/old.webp" srcset="/o 480w" data-nr-lazy="1" alt="舊">';
t('延後載入換圖', nr_native_render(mk('image',['image'=>['id'=>9]],$lz,'data-nri|5')), '<img srcset="/new-480.webp 480w, /new.webp 1200w" src="/new.webp" data-nr-lazy="1" alt="新圖 $1 ${1} 說明">');
echo "ok=$ok bad=$bad\n";
$ct2='<ol o>{{@rows icon_list}}<li a>{{.text}}</li>{{@rest}}<li b>{{.text}}</li>{{/rows}}</ol>';
t('第一列不同', nr_native_render(mk('icon-list',['icon_list'=>[['text'=>'甲'],['text'=>'乙'],['text'=>'丙']]],$ct2)), '<ol o><li a>甲</li><li b>乙</li><li b>丙</li></ol>');
echo "ok=$ok bad=$bad\n";
$tp='<p class="x">{{editor}}</p>';
t('巢狀div', nr_native_fill($tp,['editor'=>'<div><div>甲</div>乙</div>']), '<div><div>甲</div>乙</div>');
t('空巢狀', nr_native_fill($tp,['editor'=>'<div><div></div></div>']), '<div><div></div></div>');
t('巢狀表', nr_native_fill($tp,['editor'=>'<table><tr><td><table><tr><td>甲</td></tr></table>乙</td></tr></table>']), '<table><tr><td><table><tr><td>甲</td></tr></table>乙</td></tr></table>');
t('section', nr_native_fill($tp,['editor'=>'<section>甲</section>']), '<section>甲</section>');
t('巢狀後段', nr_native_fill($tp,['editor'=>'<div><p>甲</p></div><p>乙</p>']), '<div><p>甲</p></div><p class="x">乙</p>');
t('不再展開', nr_native_fill('<p>{{editor}}</p><h2>{{title}}</h2>',['editor'=>'範例 {{title}}','title'=>'替代']), '<p>範例 {{title}}</p><h2>替代</h2>');
t('列不再展開', nr_native_fill('{{@rows tabs}}<i>{{.tab_title}}</i>{{/rows}}{{title}}',['tabs'=>[['tab_title'=>'{{title}}'],null,'oops'],'title'=>'T']), '<i>{{title}}</i>T');
t('新增alt$1', nr_native_img('<img src="/old.webp">',['id'=>9],5), '<img alt="新圖 $1 ${1} 說明" srcset="/new-480.webp 480w, /new.webp 1200w" src="/new.webp">');
echo "ok=$ok bad=$bad\n";
