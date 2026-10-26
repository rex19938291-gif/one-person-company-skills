import sys,base64,json
src,els,slug,title=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
b=base64.b64encode(open(els,'rb').read()).decode()
sys.path.insert(0,'native'); import edcss
css=base64.b64encode(('.nr-sacrifice{}\n'+open('native/edcompat.css').read()+'\n'+edcss.gen(json.load(open(els)))).encode()).decode()
print(f'''$src={src}; $slug='{slug}'; $title='{title}';
$data=base64_decode('{b}');
if(json_decode($data)===null) return ['err'=>'json'];
$map=get_option('nr_native_drafts',[]); if(!is_array($map)) $map=[];
$id=isset($map[$src])?(int)$map[$src]:0;
if(!$id||!get_post($id)){{
  $id=wp_insert_post(['post_type'=>'page','post_status'=>'draft','post_title'=>$title,'post_name'=>$slug,'post_author'=>12,'post_content'=>''],true);
  if(is_wp_error($id)) return ['err'=>$id->get_error_message()];
  foreach(get_post_meta($src) as $k=>$vs){{ if(in_array($k,['_edit_lock','_edit_last','_elementor_data','_elementor_css','_wp_old_slug'],true)) continue; foreach($vs as $v) add_post_meta($id,$k,maybe_unserialize($v)); }}
  $map[$src]=$id; update_option('nr_native_drafts',$map,false);
}}
update_post_meta($id,'rank_math_robots',['noindex','nofollow']);
update_post_meta($id,'_elementor_data',wp_slash($data));
update_post_meta($id,'_elementor_edit_mode','builder');
$ps=get_post_meta($id,'_elementor_page_settings',true); if(!is_array($ps)) $ps=[]; $ps['custom_css']=base64_decode('{css}'); update_post_meta($id,'_elementor_page_settings',wp_slash($ps));
delete_post_meta($id,'_elementor_css');
if(class_exists('\\\\Elementor\\\\Plugin')) \\Elementor\\Plugin::$instance->files_manager->clear_cache();
return ['id'=>$id,'status'=>get_post_status($id),'len'=>strlen(get_post_meta($id,'_elementor_data',true)),'view'=>get_post_meta($id,'_nr_view',true),'store'=>get_post_meta($id,'_nr_store',true),'tpl'=>get_post_meta($id,'_wp_page_template',true)];''')
