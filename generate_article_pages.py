#!/usr/bin/env python3

import json
import os
from datetime import datetime
from jinja2 import Template, FileSystemLoader, Environment
from config import (
    AFFILIATE_ARTICLES_FILE, 
    OUTPUT_DIR,
    DEBUG, 
    VERBOSE
)

def load_articles_data():
    """記事データを読み込み"""
    try:
        with open(AFFILIATE_ARTICLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"記事データファイルが見つかりません: {AFFILIATE_ARTICLES_FILE}")
        return None
    except json.JSONDecodeError:
        print(f"記事データの読み込みに失敗しました: {AFFILIATE_ARTICLES_FILE}")
        return None

def setup_jinja_environment():
    """Jinja2環境をセットアップ"""
    loader = FileSystemLoader('templates')
    env = Environment(
        loader=loader,
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True
    )
    return env

def create_article_slug(article_id):
    """記事IDからスラッグを生成"""
    # 特殊文字を除去してファイル名に適した形式に変換
    slug = article_id.replace(' ', '_').replace('/', '_').replace('\\', '_')
    slug = ''.join(c for c in slug if c.isalnum() or c in '_-')
    return slug

def generate_article_page(article, template, output_dir):
    """個別記事ページを生成"""
    try:
        # HTMLを生成
        html_content = template.render(article=article)
        
        # 出力ファイルパスを作成
        slug = create_article_slug(article['id'])
        output_file = os.path.join(output_dir, 'articles', f"{slug}.html")
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # ファイルに書き込み
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        if VERBOSE:
            print(f"記事ページを生成しました: {output_file}")
        
        return output_file
    
    except Exception as e:
        print(f"記事ページの生成に失敗しました: {article.get('id', 'unknown')} - {str(e)}")
        return None

def update_main_page_links(articles_data, output_dir):
    """メインページの記事リンクを個別ページへのリンクに更新"""
    try:
        # 記事データを更新（個別ページのURLを追加）
        for article in articles_data.get('articles', []):
            slug = create_article_slug(article['id'])
            article['detail_url'] = f"articles/{slug}.html"
        
        # 更新されたデータを保存
        updated_file = os.path.join(output_dir, 'articles_with_urls.json')
        with open(updated_file, 'w', encoding='utf-8') as f:
            json.dump(articles_data, f, ensure_ascii=False, indent=2)
        
        if VERBOSE:
            print(f"記事データにURL情報を追加しました: {updated_file}")
        
        return updated_file
    
    except Exception as e:
        print(f"記事データの更新に失敗しました: {str(e)}")
        return None

def generate_sitemap_entries(articles, base_url="https://toy1021.github.io/affiliate2/"):
    """個別記事ページのサイトマップエントリを生成"""
    sitemap_entries = []
    
    for article in articles:
        slug = create_article_slug(article['id'])
        url = f"{base_url}articles/{slug}.html"
        
        # 最終更新日を取得（processed_atまたはfetched_at）
        lastmod = article.get('processed_at', article.get('fetched_at', ''))
        if lastmod:
            try:
                # ISO形式の日付をW3C Datetime形式に変換
                if 'T' in lastmod:
                    lastmod = lastmod.split('T')[0]
            except:
                lastmod = datetime.now().strftime('%Y-%m-%d')
        else:
            lastmod = datetime.now().strftime('%Y-%m-%d')
        
        sitemap_entries.append({
            'url': url,
            'lastmod': lastmod,
            'changefreq': 'monthly',
            'priority': '0.7'
        })
    
    return sitemap_entries

def update_sitemap(sitemap_entries, output_dir):
    """サイトマップに個別記事ページを追加"""
    sitemap_file = os.path.join(output_dir, 'sitemap.xml')
    
    try:
        # 既存のサイトマップを読み込み
        if os.path.exists(sitemap_file):
            with open(sitemap_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            # 基本的なサイトマップを作成
            content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://toy1021.github.io/affiliate2/</loc>
        <lastmod>{}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>'''.format(datetime.now().strftime('%Y-%m-%d'))
        
        # 個別記事のエントリを追加
        urls_xml = ""
        for entry in sitemap_entries:
            urls_xml += f'''    <url>
        <loc>{entry['url']}</loc>
        <lastmod>{entry['lastmod']}</lastmod>
        <changefreq>{entry['changefreq']}</changefreq>
        <priority>{entry['priority']}</priority>
    </url>
'''
        
        # 既存のサイトマップに新しいエントリを挿入
        if '</urlset>' in content:
            content = content.replace('</urlset>', urls_xml + '</urlset>')
        else:
            # サイトマップの形式が正しくない場合は新しく作成
            content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://toy1021.github.io/affiliate2/</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
{urls_xml}</urlset>'''
        
        # サイトマップファイルに書き込み
        with open(sitemap_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if VERBOSE:
            print(f"サイトマップを更新しました: {sitemap_file} ({len(sitemap_entries)}記事を追加)")
        
        return sitemap_file
    
    except Exception as e:
        print(f"サイトマップの更新に失敗しました: {str(e)}")
        return None

def main():
    """メイン処理"""
    print("記事個別ページの生成を開始します...")
    
    # 記事データを読み込み
    articles_data = load_articles_data()
    if not articles_data:
        print("記事データの読み込みに失敗しました。処理を終了します。")
        return
    
    articles = articles_data.get('articles', [])
    if not articles:
        print("記事データが空です。処理を終了します。")
        return
    
    print(f"記事数: {len(articles)}件")
    
    # Jinja2環境をセットアップ
    env = setup_jinja_environment()
    try:
        template = env.get_template('article.html')
    except Exception as e:
        print(f"テンプレートの読み込みに失敗しました: {str(e)}")
        return
    
    # 各記事の個別ページを生成
    generated_count = 0
    failed_count = 0
    
    for article in articles:
        output_file = generate_article_page(article, template, OUTPUT_DIR)
        if output_file:
            generated_count += 1
        else:
            failed_count += 1
    
    print(f"記事ページ生成完了: 成功 {generated_count}件, 失敗 {failed_count}件")
    
    # メインページの記事データを更新
    update_main_page_links(articles_data, OUTPUT_DIR)
    
    # サイトマップを更新
    sitemap_entries = generate_sitemap_entries(articles)
    update_sitemap(sitemap_entries, OUTPUT_DIR)
    
    print("記事個別ページの生成が完了しました。")

if __name__ == "__main__":
    main()