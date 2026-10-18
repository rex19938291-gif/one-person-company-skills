// 用法：ZBTAG＝備份標籤。先完整檢查備份，再逐頁寫回，逐值核對資料與頁面設定。
$tag='ZBTAG';
$bf=get_option('zb_native_backup_'.$tag); if(!$bf||!is_file($bf)) return ['err'=>'no backup'];
$b=unserialize(substr(file_get_contents($bf),14),['allowed_classes'=>false]);
if(!is_array($b)||!$b) return ['err'=>'bad backup'];
foreach($b as $id=>$x){
  if(!is_array($x)) return ['err'=>'corrupt '.$id];
  foreach(['data','md5','ps','psmd5','psexists'] as $k) if(!array_key_exists($k,$x)) return ['err'=>'missing '.$k.' '.$id];
  if(!is_string($x['data']) || md5($x['data'])!==$x['md5'] || json_decode($x['data'])===null) return ['err'=>'data '.$id];
  if(md5(serialize($x['ps']))!==$x['psmd5']) return ['err'=>'ps '.$id];
  if(!is_bool($x['psexists'])) return ['err'=>'psexists type '.$id];
  if(!get_post($id)) return ['err'=>'nopost '.$id];
}
$out=[];
foreach($b as $id=>$x){
  update_post_meta($id,'_elementor_data',wp_slash($x['data']));
  if($x['psexists']) update_post_meta($id,'_elementor_page_settings',wp_slash($x['ps'])); else delete_post_meta($id,'_elementor_page_settings');
  delete_post_meta($id,'_elementor_css');
  global $wpdb; $wpdb->update($wpdb->posts,['post_modified'=>current_time('mysql'),'post_modified_gmt'=>current_time('mysql',1)],['ID'=>$id]); clean_post_cache($id);
  $out[$id]=['data'=>md5(get_post_meta($id,'_elementor_data',true))===$x['md5'],'ps'=>md5(serialize(get_post_meta($id,'_elementor_page_settings',true)))===$x['psmd5'],'exists'=>metadata_exists('post',$id,'_elementor_page_settings')===$x['psexists']];
}
\Elementor\Plugin::$instance->files_manager->clear_cache();
if(function_exists('rocket_clean_minify')) rocket_clean_minify(['css','js']);
if(function_exists('rocket_clean_domain')) rocket_clean_domain();
return $out;
