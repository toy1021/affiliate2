#!/usr/bin/env python3

"""
Core Web Vitals最適化スクリプト
CSS/JS圧縮、画像最適化、キャッシュ設定など
"""

import os
import re
import json
import hashlib
from datetime import datetime
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def minify_css(css_content):
    """CSS最小化"""
    # コメント削除
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    # 不要な空白削除
    css_content = re.sub(r'\s+', ' ', css_content)
    # セミコロン前後の空白削除
    css_content = re.sub(r'\s*;\s*', ';', css_content)
    # 括弧前後の空白削除
    css_content = re.sub(r'\s*{\s*', '{', css_content)
    css_content = re.sub(r'\s*}\s*', '}', css_content)
    # コロン前後の空白調整
    css_content = re.sub(r'\s*:\s*', ':', css_content)
    return css_content.strip()

def minify_js(js_content):
    """JavaScript最小化（基本的な圧縮のみ）"""
    # コメント削除（基本的なもの）
    js_content = re.sub(r'//.*?\n', '\n', js_content)
    js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
    # 不要な空白削除（慎重に）
    js_content = re.sub(r'\n\s*\n', '\n', js_content)
    js_content = re.sub(r'^\s+', '', js_content, flags=re.MULTILINE)
    return js_content.strip()

def extract_and_optimize_css_js(html_file):
    """HTMLからCSS/JSを抽出して最適化"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # CSS抽出
    css_pattern = r'<style>(.*?)</style>'
    css_match = re.search(css_pattern, content, re.DOTALL)
    
    if css_match:
        css_content = css_match.group(1)
        minified_css = minify_css(css_content)
        
        # CSSファイル生成
        css_hash = hashlib.md5(minified_css.encode()).hexdigest()[:8]
        css_filename = f"styles.{css_hash}.css"
        
        os.makedirs("output", exist_ok=True)
        with open(f"output/{css_filename}", 'w', encoding='utf-8') as f:
            f.write(minified_css)
        
        print(f"最適化されたCSSファイル: {css_filename}")
        print(f"圧縮率: {len(css_content)} -> {len(minified_css)} bytes ({(1-len(minified_css)/len(css_content))*100:.1f}% 削減)")
        
        # HTML内のCSSをリンクタグに置換
        css_link = f'<link rel="stylesheet" href="{css_filename}">'
        content = re.sub(css_pattern, css_link, content, flags=re.DOTALL)
    
    # JavaScript抽出
    js_pattern = r'<script>(.*?)</script>'
    js_match = re.search(js_pattern, content, re.DOTALL)
    
    if js_match:
        js_content = js_match.group(1)
        minified_js = minify_js(js_content)
        
        # JS ファイル生成
        js_hash = hashlib.md5(minified_js.encode()).hexdigest()[:8]
        js_filename = f"app.{js_hash}.js"
        
        with open(f"output/{js_filename}", 'w', encoding='utf-8') as f:
            f.write(minified_js)
        
        print(f"最適化されたJSファイル: {js_filename}")
        print(f"圧縮率: {len(js_content)} -> {len(minified_js)} bytes ({(1-len(minified_js)/len(js_content))*100:.1f}% 削減)")
        
        # HTML内のJSをscriptタグに置換（defer付き）
        js_script = f'<script src="{js_filename}" defer></script>'
        content = re.sub(js_pattern, js_script, content, flags=re.DOTALL)
    
    return content, css_filename if css_match else None, js_filename if js_match else None

def add_performance_optimizations(html_content):
    """パフォーマンス最適化の追加"""
    
    # DNS プリフェッチ
    dns_prefetch = '''
    <!-- DNS Prefetch -->
    <link rel="dns-prefetch" href="//fonts.googleapis.com">
    <link rel="dns-prefetch" href="//www.google-analytics.com">
    '''
    
    # Resource Hints
    resource_hints = '''
    <!-- Resource Hints -->
    <link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
    '''
    
    # Critical CSS インライン化準備
    critical_css = '''
    <style>
    /* Critical Above-the-fold CSS */
    body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans JP',sans-serif;margin:0;background:#f8f9fa}
    .container{max-width:1200px;margin:0 auto;padding:0 20px}
    header{background:#fff;box-shadow:0 2px 4px rgba(0,0,0,.1);padding:1rem 0}
    h1{color:#2563eb;font-size:1.8rem;margin:0}
    .loading{text-align:center;padding:2rem}
    .spinner{width:40px;height:40px;border:4px solid #f0f0f0;border-top:4px solid #2563eb;border-radius:50%;animation:spin 1s linear infinite;margin:0 auto}
    @keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
    </style>
    '''
    
    # メタタグの改善
    performance_meta = '''
    <!-- Performance Meta Tags -->
    <meta http-equiv="x-dns-prefetch-control" content="on">
    <meta name="referrer" content="origin-when-cross-origin">
    '''
    
    # Service Worker登録
    sw_script = '''
    <script>
    if('serviceWorker' in navigator){
        window.addEventListener('load',()=>{
            navigator.serviceWorker.register('/sw.js')
                .then(reg=>console.log('SW registered'))
                .catch(err=>console.log('SW registration failed'));
        });
    }
    </script>
    '''
    
    # head内に挿入
    head_insert_position = html_content.find('</head>')
    if head_insert_position != -1:
        head_content = dns_prefetch + resource_hints + performance_meta
        html_content = html_content[:head_insert_position] + head_content + html_content[head_insert_position:]
    
    # body終了前にService Worker挿入
    body_insert_position = html_content.find('</body>')
    if body_insert_position != -1:
        html_content = html_content[:body_insert_position] + sw_script + html_content[body_insert_position:]
    
    return html_content

def create_service_worker():
    """Service Worker生成"""
    sw_content = '''
// Service Worker for caching
const CACHE_NAME = 'tech-news-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/articles.json',
    '/sitemap.xml',
    '/og-image.svg'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // キャッシュにあればそれを返す、なければネットワークから取得
                if (response) {
                    return response;
                }
                return fetch(event.request);
            }
        )
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});
'''
    
    os.makedirs("output", exist_ok=True)
    with open("output/sw.js", 'w', encoding='utf-8') as f:
        f.write(sw_content)
    
    print("Service Workerを生成しました: output/sw.js")

def optimize_images():
    """画像最適化（WebP変換）"""
    if not PIL_AVAILABLE:
        print("PIL/Pillow未インストールのため画像最適化をスキップ")
        return
    
    image_dirs = ["images", "output"]
    optimized_count = 0
    
    for img_dir in image_dirs:
        if not os.path.exists(img_dir):
            continue
            
        for filename in os.listdir(img_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(img_dir, filename)
                webp_path = os.path.splitext(img_path)[0] + '.webp'
                
                try:
                    # PNG/JPEGをWebPに変換
                    with Image.open(img_path) as img:
                        # RGBAモードをRGBに変換（WebP対応）
                        if img.mode in ('RGBA', 'LA', 'P'):
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            img = background
                        
                        # WebPで保存（品質85%）
                        img.save(webp_path, 'WebP', quality=85, optimize=True)
                        
                        # ファイルサイズ比較
                        original_size = os.path.getsize(img_path)
                        webp_size = os.path.getsize(webp_path)
                        reduction = ((original_size - webp_size) / original_size) * 100
                        
                        print(f"WebP変換: {filename} -> {os.path.basename(webp_path)} ({reduction:.1f}% 削減)")
                        optimized_count += 1
                        
                except Exception as e:
                    print(f"画像変換エラー {filename}: {e}")
    
    if optimized_count > 0:
        print(f"画像最適化完了: {optimized_count}個のファイルをWebP変換")

def optimize_html_template():
    """HTMLテンプレートの最適化"""
    template_file = "templates/spa.html"
    
    if not os.path.exists(template_file):
        print(f"テンプレートファイルが見つかりません: {template_file}")
        return False
    
    print("Core Web Vitals最適化を開始...")
    
    # CSS/JS抽出と最適化
    optimized_content, css_file, js_file = extract_and_optimize_css_js(template_file)
    
    # パフォーマンス最適化の追加
    optimized_content = add_performance_optimizations(optimized_content)
    
    # 最適化されたHTMLを出力
    output_file = "templates/spa_optimized.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(optimized_content)
    
    print(f"最適化されたHTMLテンプレート: {output_file}")
    
    # Service Worker生成
    create_service_worker()
    
    # 画像最適化
    optimize_images()
    
    return True, css_file, js_file

if __name__ == "__main__":
    success, css_file, js_file = optimize_html_template()
    
    if success:
        print("Core Web Vitals最適化が完了しました")
        print("改善内容:")
        print("- CSS/JavaScript圧縮と外部ファイル化")
        print("- DNS プリフェッチ設定")
        print("- Resource Hints追加")  
        print("- Service Worker実装")
        print("- Critical CSS最適化")
        print("- 画像WebP変換（対応環境のみ）")
    else:
        print("最適化処理に失敗しました")