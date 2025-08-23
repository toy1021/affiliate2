#!/usr/bin/env python3

"""
XMLサイトマップ生成スクリプト
Google検索での発見性を向上させるためのサイトマップを生成
"""

import json
import os
from datetime import datetime, timezone
from urllib.parse import quote

def generate_xml_sitemap():
    """XMLサイトマップを生成"""
    
    # サイト基本情報
    base_url = "https://toy1021.github.io/affiliate2"
    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    
    # 記事データ読み込み
    articles_file = "docs/articles.json"
    if not os.path.exists(articles_file):
        print(f"❌ 記事ファイルが見つかりません: {articles_file}")
        return False
    
    with open(articles_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    articles = data.get("articles", [])
    
    # XMLサイトマップ生成
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # 1. メインページ（最高優先度）
    xml_content.append('  <url>')
    xml_content.append(f'    <loc>{base_url}/</loc>')
    xml_content.append(f'    <lastmod>{current_time}</lastmod>')
    xml_content.append('    <changefreq>hourly</changefreq>')
    xml_content.append('    <priority>1.0</priority>')
    xml_content.append('  </url>')
    
    # 2. カテゴリページ（高優先度）
    categories = data.get("categories", [])
    for category in categories:
        cat_name = category.get("name", "")
        if cat_name:
            # URLエンコーディング
            encoded_cat = quote(cat_name)
            xml_content.append('  <url>')
            xml_content.append(f'    <loc>{base_url}/#category={encoded_cat}</loc>')
            xml_content.append(f'    <lastmod>{current_time}</lastmod>')
            xml_content.append('    <changefreq>daily</changefreq>')
            xml_content.append('    <priority>0.8</priority>')
            xml_content.append('  </url>')
    
    # 3. 記事ページ（中優先度）
    # 最新50記事のみを含める（重要記事のみ）
    top_articles = articles[:50] if len(articles) > 50 else articles
    
    for article in top_articles:
        # 記事のユニークID生成（タイトルのハッシュ）
        title = article.get("title", "")
        if title:
            import hashlib
            article_id = hashlib.md5(title.encode()).hexdigest()[:8]
            
            # 記事の公開日取得
            published = article.get("published_date", current_time)
            if published and published != "":
                # ISO format に変換
                try:
                    if "T" not in published:
                        # 日付のみの場合は時刻を追加
                        published += "T00:00:00+00:00"
                    elif "+" not in published and "Z" not in published:
                        # タイムゾーン情報がない場合は追加
                        published += "+00:00"
                except:
                    published = current_time
            else:
                published = current_time
            
            xml_content.append('  <url>')
            xml_content.append(f'    <loc>{base_url}/#article={article_id}</loc>')
            xml_content.append(f'    <lastmod>{published}</lastmod>')
            xml_content.append('    <changefreq>weekly</changefreq>')
            xml_content.append('    <priority>0.6</priority>')
            xml_content.append('  </url>')
    
    xml_content.append('</urlset>')
    
    # ファイル出力
    sitemap_content = '\n'.join(xml_content)
    
    # 複数の場所に出力
    output_files = [
        "sitemap.xml",
        "docs/sitemap.xml", 
        "output/sitemap.xml"
    ]
    
    for output_file in output_files:
        # ディレクトリ作成
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(sitemap_content)
            print(f"✅ サイトマップを生成しました: {output_file}")
        except Exception as e:
            print(f"❌ サイトマップ生成エラー: {output_file} - {e}")
    
    # 統計情報表示
    total_urls = 1 + len(categories) + len(top_articles)  # メイン + カテゴリ + 記事
    print(f"📊 サイトマップ統計:")
    print(f"   - 総URL数: {total_urls}")
    print(f"   - メインページ: 1")
    print(f"   - カテゴリページ: {len(categories)}")
    print(f"   - 記事ページ: {len(top_articles)}")
    
    return True

if __name__ == "__main__":
    print("🗺️ XMLサイトマップを生成中...")
    success = generate_xml_sitemap()
    
    if success:
        print("✅ XMLサイトマップの生成が完了しました")
    else:
        print("❌ XMLサイトマップの生成に失敗しました")