<?php
/**
 * Plugin Name: 臨時後台畫面存檔
 * Description: 管理員與 nonce 保護，只接收已去個資的畫面；完成後停用。
 * 在站方設定檔定義 TUTORIAL_DUMP_DIR 為不可公開讀取的絕對目錄。
 */
if (!defined('ABSPATH')) { exit; }
add_action('wp_ajax_tutorial_dom_dump', function () {
    if (!current_user_can('manage_options')) { wp_send_json_error('forbidden', 403); }
    check_ajax_referer('tutorial_dom_dump', 'nonce');
    if (!defined('TUTORIAL_DUMP_DIR') || !is_dir(TUTORIAL_DUMP_DIR) || !is_writable(TUTORIAL_DUMP_DIR)) {
        wp_send_json_error('private directory required', 500);
    }
    $name = sanitize_file_name(wp_unslash($_POST['name'] ?? ''));
    $source = wp_unslash($_POST['html'] ?? '');
    if (!$name || strlen($source) < 100 || strlen($source) > 8000000 || !class_exists('DOMDocument')) {
        wp_send_json_error('bad input or missing DOM extension', 400);
    }
    $doc = new DOMDocument();
    $old = libxml_use_internal_errors(true);
    try {
        if (!$doc->loadHTML('<?xml encoding="UTF-8">' . $source, LIBXML_NONET)) {
            wp_send_json_error('invalid HTML', 400);
        }
        $xpath = new DOMXPath($doc);
        foreach ($xpath->query('//script | //input[contains(translate(@name,"NONCE","nonce"),"nonce")] | //input[translate(@type,"PASSWORD","password")="password"] | //base | //iframe | //object | //embed') as $node) {
            $node->parentNode->removeChild($node);
        }
        foreach ($xpath->query('//*') as $node) {
            $remove = [];
            foreach ($node->attributes as $attribute) {
                if (preg_match('/^on|nonce/i', $attribute->name)) { $remove[] = $attribute->name; }
            }
            foreach ($remove as $attribute) { $node->removeAttribute($attribute); }
            if ($node->nodeName === 'form') { $node->removeAttribute('action'); }
        }
        // 防止原網站連結被離線點擊；保留選單結構與文字。
        foreach ($xpath->query('//a[@href]') as $node) { $node->setAttribute('href', '#'); }
        foreach ($xpath->query('//processing-instruction()') as $node) { $node->parentNode->removeChild($node); }
        $clean = $doc->saveHTML();
    } finally {
        libxml_clear_errors(); libxml_use_internal_errors($old);
    }
    // 首行先退出，即使存檔誤落網站目錄也不提供 HTML；仍必須用站外私有目錄。
    $file = rtrim(TUTORIAL_DUMP_DIR, '/\\') . DIRECTORY_SEPARATOR . $name . '-' . wp_generate_password(16, false, false) . '.php';
    $written = file_put_contents($file, "<?php exit; ?>\n" . $clean, LOCK_EX);
    if ($written === false) { wp_send_json_error('write failed', 500); }
    chmod($file, 0600);
    wp_send_json_success(['file' => basename($file), 'bytes' => $written]);
});
add_action('admin_footer', function () {
    if (current_user_can('manage_options')) {
        echo '<script>window.__tutorialDumpNonce=' . wp_json_encode(wp_create_nonce('tutorial_dom_dump')) . ';</script>';
    }
});
