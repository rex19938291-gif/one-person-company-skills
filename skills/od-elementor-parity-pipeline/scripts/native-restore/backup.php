// 用法：$ids 由呼叫端替換（NRIDS）。備份 _elementor_data 與頁面設定，寫入成功並讀回核對後才更新指標。
$ids=NRIDS; $tag='NRTAG';
$dir=WP_CONTENT_DIR.'/updraft/site-vault-20261017/native-cutover/';
if(!is_dir($dir) && !wp_mkdir_p($dir)) return ['err'=>'mkdir'];
$b=[];
foreach($ids as $id){ $d=get_post_meta($id,'_elementor_data',true); $ps=get_post_meta($id,'_elementor_page_settings',true);
  if(!is_string($d)||json_decode($d)===null) return ['err'=>'bad data '.$id];
  $b[$id]=['data'=>$d,'ps'=>$ps,'psexists'=>metadata_exists('post',$id,'_elementor_page_settings'),'md5'=>md5($d),'psmd5'=>md5(serialize($ps))]; }
$f=$dir.'backup-'.$tag.'-'.date('Ymd-His').'.php';
$body='<?php exit; ?>'.serialize($b);
if(file_put_contents($f,$body)!==strlen($body)) return ['err'=>'write'];
$chk=unserialize(substr(file_get_contents($f),14),['allowed_classes'=>false]);
foreach($ids as $id){ if(!isset($chk[$id]) || $chk[$id]['md5']!==md5(get_post_meta($id,'_elementor_data',true)) || $chk[$id]['psmd5']!==md5(serialize(get_post_meta($id,'_elementor_page_settings',true)))) return ['err'=>'verify '.$id]; }
update_option('nr_native_backup_'.$tag,$f,false);
return ['file'=>$f,'n'=>count($chk),'size'=>filesize($f)];
