// 用法：NRPAIRS＝[[目標ID,來源草稿ID],...]。先全部檢查，再寫入；頁面設定只換 custom_css；寫入後逐值核對。
$pairs=NRPAIRS; $tag='NRTAG';
$bf=get_option('nr_native_backup_'.$tag); if(!$bf||!is_file($bf)) return ['err'=>'no backup'];
$plan=[];
foreach($pairs as [$id,$src]){ $data=get_post_meta($src,'_elementor_data',true); if(!is_string($data)||json_decode($data)===null) return ['err'=>'json '.$src];
  $dps=get_post_meta($src,'_elementor_page_settings',true); $ps=get_post_meta($id,'_elementor_page_settings',true); if(!is_array($ps)) $ps=[];
  $ps['custom_css']=is_array($dps)?($dps['custom_css']??''):''; $plan[$id]=[$data,$ps]; }
$out=[];
foreach($plan as $id=>[$data,$ps]){
  update_post_meta($id,'_elementor_data',wp_slash($data));
  update_post_meta($id,'_elementor_page_settings',wp_slash($ps));
  delete_post_meta($id,'_elementor_css');
  // 更新頁面修改時間，避免編輯器把較舊內容的自動暫存當成「較新」而提示還原
  global $wpdb; $now=current_time('mysql'); $gmt=current_time('mysql',1);
  $wpdb->update($wpdb->posts,['post_modified'=>$now,'post_modified_gmt'=>$gmt],['ID'=>$id]); clean_post_cache($id);
  $as=wp_get_post_autosave($id); $asnew=$as && strtotime($as->post_modified_gmt) >= strtotime($gmt);
  $out[$id]=['autosave_newer'=>$asnew]+['data'=>get_post_meta($id,'_elementor_data',true)===$data,'ps'=>get_post_meta($id,'_elementor_page_settings',true)===$ps];
}
\Elementor\Plugin::$instance->files_manager->clear_cache();
if(function_exists('rocket_clean_minify')) rocket_clean_minify(['css','js']);
if(function_exists('rocket_clean_domain')) rocket_clean_domain();
return $out;
