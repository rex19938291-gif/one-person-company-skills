<?php
/**
 * 站點外掛片段（參考實作）：原生 Elementor 元件 → 前台組回原本的網頁結構（2026-10-17）。
 * 新專案請改：函式前綴 nr_、站點判斷 nr_site_render()／nr_site_view()、下方常數 NR_BRAND_NAME／NR_IG_TEMPLATE_ID／NR_IG_USERNAME。
 * 只處理 _css_classes 含 nr-n 的元件；元件的 Pro 自訂屬性 data-nrt 存原本的網頁碼樣板（base64），
 * 樣板裡的 {{設定路徑}} 由元件目前的設定值帶入，業主在面板改字、換圖、改連結，前台就跟著變。
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
if ( ! defined( 'NR_BRAND_NAME' ) ) {
	define( 'NR_BRAND_NAME', '品牌名稱' ); // 麵包屑第一層名稱
}
if ( ! defined( 'NR_IG_TEMPLATE_ID' ) ) {
	define( 'NR_IG_TEMPLATE_ID', 0 ); // WP Social Ninja 的 IG 版型 ID
}
if ( ! defined( 'NR_IG_USERNAME' ) ) {
	define( 'NR_IG_USERNAME', 'brand_ig_account' ); // 優先切換到的 IG 帳號
}

function nr_native_is( $el ) {
	return 'widget' === $el->get_type() && false !== strpos( ' ' . (string) $el->get_settings( '_css_classes' ) . ' ', ' nr-n ' );
}

/** 讀 Pro 自訂屬性（key|value 一行一個） */
function nr_native_attrs( $el ) {
	$out = array();
	foreach ( preg_split( '/\r?\n/', (string) $el->get_settings( '_attributes' ) ) as $line ) {
		$p = strpos( $line, '|' );
		if ( false !== $p ) {
			$out[ trim( substr( $line, 0, $p ) ) ] = substr( $line, $p + 1 );
		}
	}
	return $out;
}

function nr_native_get( $s, $path ) {
	foreach ( explode( '.', $path ) as $k ) {
		if ( is_array( $s ) && array_key_exists( $k, $s ) ) {
			$s = $s[ $k ];
		} else {
			return '';
		}
	}
	return $s;
}

/** 連結：只取網址，擋掉 javascript: 之類不安全的協定 */
function nr_native_url( $v ) {
	$u = is_array( $v ) ? (string) ( $v['url'] ?? '' ) : (string) $v;
	if ( '' === $u || '' === esc_url_raw( $u ) ) {
		return '';
	}
	return esc_attr( $u );
}

/** 文字編輯器內容：只有一段且沒有區塊標籤時拿掉外層 <p>；否則回傳 null，交給逐段輸出 */
function nr_native_inline( $h ) {
	$h = trim( (string) $h );
	if ( preg_match( '#^<p>(.*)</p>$#s', $h, $m ) ) {
		$h = $m[1];
	}
	if ( preg_match( '#<(?!/?(?:a|span|strong|em|b|i|u|s|br|small|mark|sup|sub|img|code|wbr|abbr|time|del|ins|q|cite)\b)[a-z]#i', $h ) ) {
		return null;
	}
	return $h;
}

/** 多段或含區塊的內容：用 DOM 解析最外層節點；最外層 <p> 套原本段落的開頭標籤，連續的行內內容合成一段，其他區塊原樣保留（巢狀也不拆） */
function nr_native_blocks( $open, $h ) {
	$h = trim( (string) $h );
	if ( '' === $h ) {
		return '';
	}
	$doc  = new \DOMDocument();
	$prev = libxml_use_internal_errors( true );
	$doc->loadHTML( '<?xml encoding="utf-8"?><div id="nr-native-root">' . $h . '</div>', LIBXML_HTML_NOIMPLIED | LIBXML_HTML_NODEFDTD );
	libxml_clear_errors();
	libxml_use_internal_errors( $prev );
	$root = $doc->getElementById( 'nr-native-root' );
	if ( ! $root ) {
		return $open . $h . '</p>';
	}
	$inline = array( 'a', 'span', 'strong', 'em', 'b', 'i', 'u', 's', 'br', 'small', 'mark', 'sup', 'sub', 'img', 'code', 'wbr', 'abbr', 'time', 'del', 'ins', 'q', 'cite' );
	$out    = '';
	$run    = '';
	$flush  = function () use ( &$run, &$out, $open ) {
		if ( '' !== trim( strip_tags( $run, '<img>' ) ) ) {
			$out .= $open . trim( $run ) . '</p>';
		}
		$run = '';
	};
	foreach ( iterator_to_array( $root->childNodes ) as $n ) {
		$is_el = XML_ELEMENT_NODE === $n->nodeType;
		$tag   = $is_el ? strtolower( $n->nodeName ) : '';
		if ( ! $is_el || in_array( $tag, $inline, true ) ) {
			$run .= $doc->saveHTML( $n );
			continue;
		}
		$flush();
		if ( 'p' === $tag ) {
			$in = '';
			foreach ( iterator_to_array( $n->childNodes ) as $c ) {
				$in .= $doc->saveHTML( $c );
			}
			if ( '' !== trim( strip_tags( $in, '<img>' ) ) ) {
				$out .= $open . $in . '</p>';
			}
		} else {
			$out .= $doc->saveHTML( $n );
		}
	}
	$flush();
	return $out;
}

/** 富文字欄位（editor／tab_content）：放回原段落；內容有多段或清單時改逐段輸出 */
function nr_native_rich( $tpl, $get ) {
	return preg_replace_callback(
		'#(<p\b[^>]*>)\{\{(\.?[a-z0-9_.]*(?:editor|tab_content))\}\}</p>#i',
		function ( $m ) use ( $get ) {
			$v   = (string) $get( $m[2] );
			$one = nr_native_inline( $v );
			return nr_native_guard( null === $one ? nr_native_blocks( $m[1], $v ) : $m[1] . $one . '</p>' );
		},
		$tpl
	);
}

/** 帶入內容裡的 {{ 先換成不會被當佔位字的記號，最後再換回 */
function nr_native_guard( $v ) {
	return str_replace( '{{', "{\x01{", (string) $v );
}

/** 樣板帶入：{{路徑}}、{{@rows 欄位}}…{{/rows}}（依目前項目逐列）、列內 {{.鍵}}、{{.#zh}}（一二三）、{{.#n}} */
function nr_native_fill( $tpl, $s ) {
	$tpl = preg_replace_callback(
		'#\{\{@rows ([a-z0-9_]+)\}\}(.*?)\{\{/rows\}\}#is',
		function ( $m ) use ( $s ) {
			$items = isset( $s[ $m[1] ] ) && is_array( $s[ $m[1] ] ) ? array_values( $s[ $m[1] ] ) : array();
			$zh    = array( '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二' );
			$out   = '';
			// 第一列與其他列樣式不同時，樣板寫成「第一列{{@rest}}其他列」
			$parts = explode( '{{@rest}}', $m[2], 2 );
			foreach ( $items as $i => $it ) {
				if ( ! is_array( $it ) ) {
					continue; // 不是正常項目就略過
				}
				$get  = function ( $k ) use ( $it ) {
					return nr_native_get( $it, ltrim( $k, '.' ) );
				};
				$one  = ( 0 === $i || ! isset( $parts[1] ) ) ? $parts[0] : $parts[1];
				$row  = nr_native_rich( $one, $get );
				$row  = preg_replace_callback(
					'#\{\{\.(\#zh|\#n|[a-z0-9_.]+)\}\}#i',
					function ( $x ) use ( $it, $i, $zh ) {
						if ( '#zh' === $x[1] ) {
							return $zh[ $i ] ?? (string) ( $i + 1 );
						}
						if ( '#n' === $x[1] ) {
							return (string) ( $i + 1 );
						}
						$v = nr_native_get( $it, $x[1] );
						return nr_native_guard( is_array( $v ) ? nr_native_url( $v ) : (string) $v );
					},
					$row
				);
				$out .= $row;
			}
			return $out;
		},
		$tpl
	);
	$tpl = nr_native_rich(
		$tpl,
		function ( $k ) use ( $s ) {
			return nr_native_get( $s, $k );
		}
	);
	$tpl = preg_replace_callback(
		'/\{\{([a-z0-9_.]+)\}\}/i',
		function ( $m ) use ( $s ) {
			$v = nr_native_get( $s, $m[1] );
			return nr_native_guard( is_array( $v ) ? nr_native_url( $v ) : (string) $v );
		},
		$tpl
	);
	return str_replace( "{\x01{", '{{', $tpl );
}

/** 換掉 <img> 的某個屬性（用回呼，值裡的 $1 不會被當成參照）；沒有就加上 */
function nr_native_set_attr( $img, $name, $val ) {
	$q = esc_attr( $val );
	$n = 0;
	$img = preg_replace_callback( '/\s' . preg_quote( $name, '/' ) . '="[^"]*"/', function () use ( $name, $q ) { return ' ' . $name . '="' . $q . '"'; }, $img, 1, $n );
	return $n ? $img : preg_replace_callback( '/^<img\b/', function () use ( $name, $q ) { return '<img ' . $name . '="' . $q . '"'; }, $img );
}

/** 照片：沒換圖輸出原本網頁碼；換成媒體庫其他照片或外部網址就改 src／srcset／alt；清除照片就不輸出 */
function nr_native_img( $html, $img, $orig_id ) {
	$id  = isset( $img['id'] ) ? (int) $img['id'] : 0;
	$url = isset( $img['url'] ) ? (string) $img['url'] : '';
	if ( $id && $id === (int) $orig_id ) {
		return $html;
	}
	if ( ! $id && '' === $url ) {
		return preg_replace( '/<img\b[^>]*>/', '', $html, 1 );
	}
	$src = $id ? (string) wp_get_attachment_image_url( $id, 'full' ) : '';
	if ( '' === $src ) {
		$src = $url;
	}
	if ( '' === esc_url_raw( $src ) ) {
		return $html;
	}
	$set = $id ? (string) wp_get_attachment_image_srcset( $id, 'full' ) : '';
	$alt = $id ? trim( (string) get_post_meta( $id, '_wp_attachment_image_alt', true ) ) : '';
	if ( '' === $alt && isset( $img['alt'] ) ) {
		$alt = (string) $img['alt'];
	}
	return preg_replace_callback(
		'/<img\b[^>]*>/',
		function ( $m ) use ( $src, $set, $alt ) {
			$t    = $m[0];
			$lazy = false !== strpos( $t, ' data-nr-src="' ) || false !== strpos( $t, 'data-nr-lazy="1"' );
			$t    = preg_replace( '/\s(?:data-nr-|data-nr-h)?srcset="[^"]*"/', '', $t );
			$t    = preg_replace( '/\s(?:data-nr-|data-nr-h)src="[^"]*"/', '', $t );
			$t    = nr_native_set_attr( $t, 'src', $src );
			if ( $set ) {
				$t = nr_native_set_attr( $t, 'srcset', $set );
			}
			if ( $lazy && false === strpos( $t, 'data-nr-lazy="1"' ) ) {
				$t = preg_replace( '/^<img\b/', '<img data-nr-lazy="1"', $t );
			}
			return nr_native_set_attr( $t, 'alt', $alt );
		},
		$html,
		1
	);
}

function nr_native_render( $el ) {
	$a   = nr_native_attrs( $el );
	$tpl = isset( $a['data-nrt'] ) ? base64_decode( $a['data-nrt'] ) : '';
	if ( '' === $tpl ) {
		return null;
	}
	$s    = $el->get_settings_for_display();
	$html = nr_native_fill( $tpl, is_array( $s ) ? $s : array() );
	if ( 'image' === $el->get_name() ) {
		$html = nr_native_img( $html, isset( $s['image'] ) && is_array( $s['image'] ) ? $s['image'] : array(), isset( $a['data-nri'] ) ? $a['data-nri'] : 0 );
	}
	return $html;
}

add_action(
	'elementor/frontend/before_render',
	function ( $el ) {
		if ( function_exists( 'nr_site_render' ) && nr_site_render() && nr_native_is( $el ) ) {
			ob_start();
			$GLOBALS['nr_native_ob'][ spl_object_id( $el ) ] = ob_get_level();
		}
	},
	1
);
add_action(
	'elementor/frontend/after_render',
	function ( $el ) {
		$k = spl_object_id( $el );
		if ( ! isset( $GLOBALS['nr_native_ob'][ $k ] ) ) {
			return;
		}
		$lvl = $GLOBALS['nr_native_ob'][ $k ];
		unset( $GLOBALS['nr_native_ob'][ $k ] );
		if ( ob_get_level() !== $lvl ) {
			return; // 緩衝層數不對（被其他程式動過），不碰別人的緩衝
		}
		$orig = ob_get_clean();
		try {
			$html = nr_native_render( $el );
			if ( null !== $html ) {
				$html = do_shortcode( $html );
			}
		} catch ( \Throwable $e ) {
			error_log( 'nr-native render: ' . $e->getMessage() );
			$html = null;
		}
		if ( null === $html ) {
			echo $orig; // phpcs:ignore
			return;
		}
		$html = preg_replace_callback(
			'/<img\\b[^>]*\\bdata-nr-lazy="1"[^>]*>/',
			function ( $m ) {
				return str_replace( array( ' srcset="', ' src="' ), array( ' data-nr-srcset="', ' data-nr-src="' ), $m[0] );
			},
			$html
		);
		if ( function_exists( 'nr_perf_rewrite' ) ) {
			$html = nr_perf_rewrite( $html );
		}
		if ( function_exists( 'nr_link_line_id' ) ) {
			$html = nr_link_line_id( $html );
		}
		echo $html; // phpcs:ignore
	},
	99
);

/* Elementor 編輯預覽（只用 Elementor 自己的預覽模式判斷）：頁面預覽補上頁首頁尾樣式；
   編輯頁首頁尾範本時也載入網站樣式，預覽才會和前台一樣。訪客看到的前台不受影響。 */
add_action(
	'wp_enqueue_scripts',
	function () {
		if ( ! class_exists( '\Elementor\Plugin' ) ) {
			return;
		}
		$p = \Elementor\Plugin::$instance;
		if ( ! ( $p->preview && $p->preview->is_preview_mode() ) ) {
			return;
		}
		$id   = get_queried_object_id();
		$tpl  = 'elementor_library' === get_post_type( $id ) && in_array( get_post_meta( $id, '_elementor_template_type', true ), array( 'header', 'footer' ), true );
		$page = function_exists( 'nr_site_view' ) && '' !== nr_site_view();
		if ( ! $tpl && ! $page ) {
			return;
		}
		$list = $tpl ? array( 'nr-fonts-core', 'nr-fonts-ext', 'nr-responsive', 'nr-site', 'nr-chrome' ) : array( 'nr-chrome' );
		foreach ( $list as $h ) {
			wp_enqueue_style( $h, NR_SITE_URL . 'assets/' . $h . '.css', array(), NR_SITE_VER . '-ed' );
		}
	},
	21
);

/* 品牌故事、人才招募、服務條款、隱私權：補輸出頁面結構化資料（2026-10-17）。
   Rank Math 的頁面結構化資料是關閉的（避免與首頁、分店頁的自訂資料重複），這四頁原本沒有任何 ld+json。
   只寫網站上已有的資訊：頁名、網址、說明、分享圖、麵包屑；publisher 指向首頁的品牌 Organization（#brand）。 */
function nr_native_page_meta( $id ) {
	$title = '';
	$desc  = '';
	$url   = get_permalink( $id );
	if ( class_exists( '\RankMath\Paper\Paper' ) ) {
		try {
			$paper = \RankMath\Paper\Paper::get();
			$title = (string) $paper->get_title();
			$desc  = (string) $paper->get_description();
			$canon = (string) $paper->get_canonical();
			if ( '' !== $canon ) {
				$url = $canon;
			}
		} catch ( \Throwable $e ) {
			$title = '';
		}
	}
	if ( '' === $title ) {
		$title = wp_get_document_title();
	}
	if ( '' === $desc ) {
		$desc = (string) get_post_meta( $id, 'rank_math_description', true );
	}
	$img = (string) get_post_meta( $id, 'rank_math_facebook_image', true );
	if ( '' === $img ) {
		$img = (string) get_the_post_thumbnail_url( $id, 'full' );
	}
	if ( '' === $img ) {
		$t   = get_option( 'rank-math-options-titles' );
		$img = is_array( $t ) && ! empty( $t['open_graph_image'] ) ? (string) $t['open_graph_image'] : '';
	}
	$dec = function ( $t ) {
		return html_entity_decode( wp_strip_all_tags( $t ), ENT_QUOTES | ENT_HTML5, 'UTF-8' );
	};
	return array( $dec( $title ), $dec( $desc ), $url, $img );
}
add_action(
	'wp_head',
	function () {
		if ( ! function_exists( 'nr_site_active' ) || ! nr_site_active() || ! in_array( nr_site_view(), array( 'story', 'career', 'legal' ), true ) ) {
			return;
		}
		$id                          = get_queried_object_id();
		list( $title, $desc, $url, $img ) = nr_native_page_meta( $id );
		$home                        = home_url( '/' );
		$page                        = array(
			'@type'      => 'story' === nr_site_view() ? array( 'WebPage', 'AboutPage' ) : 'WebPage',
			'@id'        => $url . '#webpage',
			'url'        => $url,
			'name'       => $title,
			'inLanguage' => 'zh-TW',
			'isPartOf'   => array( '@id' => $home . '#website' ),
			'publisher'  => array( '@id' => $home . '#brand' ),
			'breadcrumb' => array( '@id' => $url . '#breadcrumb' ),
		);
		if ( '' !== $desc ) {
			$page['description'] = $desc;
		}
		if ( '' !== $img ) {
			$page['primaryImageOfPage'] = array( '@type' => 'ImageObject', 'url' => $img );
		}
		$graph = array(
			'@context' => 'https://schema.org',
			'@graph'   => array(
				$page,
				array(
					'@type'           => 'BreadcrumbList',
					'@id'             => $url . '#breadcrumb',
					'itemListElement' => array(
						array( '@type' => 'ListItem', 'position' => 1, 'name' => NR_BRAND_NAME, 'item' => $home ),
						array( '@type' => 'ListItem', 'position' => 2, 'name' => html_entity_decode( wp_strip_all_tags( get_the_title( $id ) ), ENT_QUOTES | ENT_HTML5, 'UTF-8' ), 'item' => $url ),
					),
				),
			),
		);
		echo '<script type="application/ld+json">' . wp_json_encode( $graph, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_HEX_TAG ) . '</script>' . "\n"; // phpcs:ignore
	},
	3
);

/* 首頁只留一個品牌 Organization（2026-10-17）：Rank Math 另外輸出的 #organization 拿掉，
   所有指向它的 publisher 等參照改指首頁品牌 #brand（資料來源 ld.json，含三家門市）。不改 Rank Math 外掛檔。 */
add_filter(
	'rank_math/json_ld',
	function ( $data ) {
		if ( ! is_array( $data ) || ! function_exists( 'nr_site_view' ) || '' === nr_site_view() ) {
			return $data; // 只在本站自訂的頁面處理（首頁、分店、品牌故事等），其他頁面維持 Rank Math 原樣
		}
		$old = home_url( '/' ) . '#organization';
		$new = home_url( '/' ) . '#brand';
		$fix = function ( $v ) use ( &$fix, $old, $new ) {
			if ( is_array( $v ) ) {
				if ( isset( $v['@id'] ) && $old === $v['@id'] ) {
					$v['@id'] = $new; // 只改參照，其他欄位保留
				}
				foreach ( $v as $k => $x ) {
					$v[ $k ] = $fix( $x );
				}
			}
			return $v;
		};
		foreach ( $data as $k => $node ) {
			if ( is_array( $node ) && isset( $node['@id'] ) && $old === $node['@id'] ) {
				unset( $data[ $k ] ); // Rank Math 的 Organization 本體
				continue;
			}
			$data[ $k ] = $fix( $node );
		}
		return $data;
	},
	99
);

/* 簡潔後台加「頁首頁尾」入口（2026-10-17）：直接開 Elementor 編輯全站頁首、頁尾範本。
   範本 ID 依「套用到全站」的頁首／頁尾範本自動找，換範本也不用改程式。 */
function nr_native_chrome_ids() {
	$out = array();
	foreach ( array( 'header', 'footer' ) as $type ) {
		$q = get_posts(
			array(
				'post_type'      => 'elementor_library',
				'post_status'    => 'publish',
				'posts_per_page' => -1,
				'meta_key'       => '_elementor_template_type', // phpcs:ignore
				'meta_value'     => $type, // phpcs:ignore
				'fields'         => 'ids',
			)
		);
		foreach ( $q as $id ) {
			if ( in_array( 'include/general', (array) get_post_meta( $id, '_elementor_conditions', true ), true ) ) {
				$out[ $type ] = $id;
				break;
			}
		}
	}
	return $out;
}
add_action(
	'admin_menu',
	function () {
		if ( ! function_exists( 'nr_simple_admin_on' ) || ! nr_simple_admin_on() || ! current_user_can( 'edit_pages' ) ) {
			return;
		}
		$ids = nr_native_chrome_ids();
		if ( ! $ids ) {
			return;
		}
		$links = array();
		if ( ! empty( $ids['header'] ) ) {
			$links['編輯頁首'] = 'post.php?post=' . (int) $ids['header'] . '&action=elementor';
		}
		if ( ! empty( $ids['footer'] ) ) {
			$links['編輯頁尾'] = 'post.php?post=' . (int) $ids['footer'] . '&action=elementor';
		}
		$top = reset( $links );
		add_menu_page( '頁首頁尾', '頁首頁尾', 'edit_pages', $top, '', 'dashicons-layout', 21 );
		foreach ( $links as $t => $u ) {
			add_submenu_page( $top, $t, $t, 'edit_pages', $u );
		}
	},
	100000
);

/* ---------- IG 最新消息（2026-10-17）：業主自己綁帳號後自動顯示；標籤接受 #最新消息／#最新訊息（含全形＃） ---------- */
function nr_ig_norm( $s ) {
	return str_replace( '＃', '#', (string) $s );
}
/** 要比對的標籤：option nr_ig_tag 有設定（非空白）就只用它，否則 #最新消息、#最新訊息 兩種都接受 */
function nr_ig_tags() {
	$opt = trim( nr_ig_norm( (string) get_option( 'nr_ig_tag', '' ) ) );
	return '' !== $opt ? array( $opt ) : array( '#最新消息', '#最新訊息' );
}
/** 完整標籤比對：標籤後面不能緊接文字、數字或底線（避免把「#最新消息來源」當成「#最新消息」） */
function nr_ig_tag_re() {
	return '/(' . implode( '|', array_map( function ( $t ) { return preg_quote( $t, '/' ); }, nr_ig_tags() ) ) . ')(?![\p{L}\p{N}_])/iu';
}
function nr_ig_has_tag( $cap ) {
	return (bool) preg_match( nr_ig_tag_re(), nr_ig_norm( $cap ) );
}
function nr_ig_strip_tag( $cap ) {
	$out = preg_replace( nr_ig_tag_re(), '', nr_ig_norm( $cap ) );
	return trim( null === $out ? nr_ig_norm( $cap ) : $out );
}
/** 已連線的 IG 帳號（WP Social Ninja）：回傳 [帳號 id => username] */
function nr_ig_connected() {
	$cfg = get_option( 'wpsr_instagram_verification_configs' );
	$cfg = is_object( $cfg ) ? (array) $cfg : $cfg;
	$out = array();
	foreach ( (array) ( is_array( $cfg ) ? ( $cfg['connected_accounts'] ?? array() ) : array() ) as $k => $a ) {
		$a  = (array) $a;
		$id = (string) ( ! empty( $a['user_id'] ) ? $a['user_id'] : $k ); // WP Social Ninja 以帳號 ID 當鍵，每筆也存 user_id
		if ( '' !== $id ) {
			$out[ $id ] = (string) ( $a['username'] ?? '' );
		}
	}
	return $out;
}
/** 讀 IG 版型（NR_IG_TEMPLATE_ID）的設定（JSON 字串）並解碼 */
function nr_ig_tpl_cfg() {
	$c = get_post_meta( NR_IG_TEMPLATE_ID, '_wpsr_template_config', true );
	return is_string( $c ) ? json_decode( $c, true ) : ( is_array( $c ) ? $c : null );
}
/** 決定要顯示哪個帳號：範本的帳號已解除時，自動改用 NR_IG_USERNAME（沒有就用第一個已連線帳號）並寫回範本；
    沒有任何帳號、或切換沒有完整成功時回傳空字串（顯示備用文字）。
    不用鎖：切換可以重複執行（同時進來的請求寫的是同一個帳號，結果相同）；每次切換的備份用時間加隨機碼命名、不會互相覆蓋；
    寫回範本後讀回確認，確認成功才刪保底與清首頁快取。 */
function nr_ig_resolve_account( $cfg ) {
	$cur  = (string) ( $cfg['feed_settings']['source_settings']['account_ids'][0] ?? '' );
	$conn = nr_ig_connected();
	if ( ! $conn ) {
		return '';
	}
	if ( '' !== $cur && isset( $conn[ $cur ] ) ) {
		return $cur;
	}
	// 重新讀最新的範本設定（避免用到請求開頭讀到的舊設定）
	wp_cache_delete( NR_IG_TEMPLATE_ID, 'post_meta' );
	$raw = get_post_meta( NR_IG_TEMPLATE_ID, '_wpsr_template_config', true );
	$cfg = nr_ig_tpl_cfg();
	if ( ! is_array( $cfg ) ) {
		return '';
	}
	$cur = (string) ( $cfg['feed_settings']['source_settings']['account_ids'][0] ?? '' );
	if ( '' !== $cur && isset( $conn[ $cur ] ) ) {
		return $cur; // 別的請求剛換好
	}
	$new = (string) ( array_search( NR_IG_USERNAME, $conn, true ) ?: array_key_first( $conn ) );
	if ( '' === $new ) {
		return '';
	}
	// 備份：時間加隨機碼命名，不覆寫，讀回確認
	$bk  = 'nr_ig_switch_backup_' . gmdate( 'YmdHis' ) . '_' . substr( wp_generate_uuid4(), 0, 8 );
	$val = array( 'tpl' => $raw, 'lastgood' => get_option( 'nr_ig_lastgood' ), 'from' => $cur, 'to' => $new );
	if ( ! add_option( $bk, $val, '', 'no' ) || get_option( $bk ) !== $val ) {
		error_log( 'nr-ig: 備份寫入失敗，不切換帳號' );
		return '';
	}
	// 只改帳號欄位，寫回後讀回確認
	$cfg['feed_settings']['source_settings']['account_ids'] = array( $new );
	update_post_meta( NR_IG_TEMPLATE_ID, '_wpsr_template_config', wp_slash( wp_json_encode( $cfg, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) ) );
	wp_cache_delete( NR_IG_TEMPLATE_ID, 'post_meta' );
	$chk = nr_ig_tpl_cfg();
	if ( (string) ( $chk['feed_settings']['source_settings']['account_ids'][0] ?? '' ) !== $new ) {
		error_log( 'nr-ig: 範本寫回後讀回不一致，不切換帳號' );
		return '';
	}
	delete_option( 'nr_ig_lastgood' );
	if ( function_exists( 'rocket_clean_home' ) ) {
		rocket_clean_home();
	}
	if ( function_exists( 'rocket_clean_post' ) && get_option( 'page_on_front' ) ) {
		rocket_clean_post( (int) get_option( 'page_on_front' ) );
	}
	return $new;
}

/* 常見問答結構化資料改從頁面上的問答元件產生（2026-10-17）：業主在 Elementor 改問答，Google 看到的也會同步。
   只取樣板是 <details> 的問答元件（門市資訊清單不算）；問題＝標題、答案＝內容去標籤。找不到就回傳原本 ld.json 的資料。 */
function nr_native_faq_items( $post_id ) {
	$data = json_decode( (string) get_post_meta( $post_id, '_elementor_data', true ), true );
	if ( ! is_array( $data ) ) {
		return null; // 讀不到頁面資料
	}
	$found = false;
	$txt  = function ( $h ) {
		$h = preg_replace( '#<br\s*/?>|</(?:p|li|div|h[1-6]|tr|blockquote)>#i', "\n", (string) $h );
		$h = preg_replace( '#</t[dh]>#i', ' ', $h );
		$h = html_entity_decode( wp_strip_all_tags( $h ), ENT_QUOTES | ENT_HTML5, 'UTF-8' );
		$h = preg_replace( "/[ \t\x{00A0}\x{3000}]*\n[ \t\x{00A0}\x{3000}]*/u", "\n", $h ); // 只整理行首行尾空白，保留空行
		return (string) preg_replace( '/^[\s\x{00A0}\x{3000}]+|[\s\x{00A0}\x{3000}]+$/u', '', $h );
	};
	$out  = array();
	$walk = function ( $els ) use ( &$walk, &$out, $txt, &$found ) {
		foreach ( (array) $els as $e ) {
			if ( 'toggle' === ( $e['widgetType'] ?? '' ) ) {
				$tpl = '';
				foreach ( preg_split( '/\r?\n/', (string) ( $e['settings']['_attributes'] ?? '' ) ) as $l ) {
					if ( 0 === strpos( $l, 'data-nrt|' ) ) {
						$tpl = (string) base64_decode( substr( $l, 9 ) );
					}
				}
				if ( false !== strpos( $tpl, '<details' ) ) {
					$found = true;
					foreach ( (array) ( $e['settings']['tabs'] ?? array() ) as $it ) {
						$q = $txt( $it['tab_title'] ?? '' );
						$a = $txt( $it['tab_content'] ?? '' );
						if ( '' !== $q && '' !== $a ) {
							$out[] = array( $q, $a );
						}
					}
				}
			}
			$walk( $e['elements'] ?? array() );
		}
	};
	$walk( $data );
	return $found ? $out : null; // null＝頁面上沒有問答元件；空陣列＝有元件但題目都刪光了
}
/** 回傳新的 FAQPage；頁面沒有問答元件時回傳原本的 $faq（ld.json 備援）；問答被刪光時回傳 null（不要輸出 FAQPage） */
function nr_native_faq_ld( $faq, $post_id ) {
	$items = nr_native_faq_items( $post_id );
	if ( null === $items || ! is_array( $faq ) ) {
		return $faq;
	}
	if ( ! $items ) {
		return null;
	}
	$faq['mainEntity'] = array();
	foreach ( $items as $qa ) {
		$faq['mainEntity'][] = array( '@type' => 'Question', 'name' => $qa[0], 'acceptedAnswer' => array( '@type' => 'Answer', 'text' => $qa[1] ) );
	}
	return $faq;
}

/* 分店頁：輸出這間店的 FAQPage（從頁面上的問答元件產生），用 @id 和該頁 Restaurant 互相參照 */
add_action(
	'wp_head',
	function () {
		if ( ! function_exists( 'nr_site_active' ) || ! nr_site_active() || 'store' !== nr_site_view() ) {
			return;
		}
		$id  = get_queried_object_id();
		$url = get_permalink( $id );
		$faq = nr_native_faq_ld( array( '@context' => 'https://schema.org', '@type' => 'FAQPage', '@id' => $url . '#faq', 'about' => array( '@id' => $url . '#restaurant' ), 'mainEntity' => array() ), $id );
		if ( ! is_array( $faq ) || empty( $faq['mainEntity'] ) ) { // 分店沒有 ld.json 備援：沒有問答就不輸出
			return;
		}
		echo '<script type="application/ld+json">' . wp_json_encode( $faq, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_HEX_TAG ) . '</script>' . "\n"; // phpcs:ignore
	},
	3
);
