#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def generate_sitemap():
    """XMLサイトマップを生成"""
    
    # サイト情報を読み込み
    if os.path.exists('output/sitemap.json'):
        with open('output/sitemap.json', 'r', encoding='utf-8') as f:
            site_data = json.load(f)
    else:
        print("Error: sitemap.json not found")
        return
    
    # XML要素を作成
    urlset = Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:news', 'http://www.google.com/schemas/sitemap-news/0.9')
    
    base_url = 'https://toy1021.github.io/affiliate2/'
    last_mod = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')
    
    # トップページ
    url = SubElement(urlset, 'url')
    SubElement(url, 'loc').text = base_url
    SubElement(url, 'lastmod').text = last_mod
    SubElement(url, 'changefreq').text = 'daily'
    SubElement(url, 'priority').text = '1.0'
    
    # 各ページ
    for page_num in range(2, site_data['total_pages'] + 1):
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = f"{base_url}page{page_num}.html"
        SubElement(url, 'lastmod').text = last_mod
        SubElement(url, 'changefreq').text = 'daily'
        SubElement(url, 'priority').text = '0.8'
    
    # 記事データを読み込み（最新記事用）
    if os.path.exists('output/processed_articles.json'):
        with open('output/processed_articles.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        # 最新記事のニュースサイトマップエントリを追加
        for article in articles[:50]:  # 最新50記事
            url = SubElement(urlset, 'url')
            SubElement(url, 'loc').text = article.get('link', '')
            SubElement(url, 'lastmod').text = last_mod
            SubElement(url, 'changefreq').text = 'never'
            SubElement(url, 'priority').text = '0.6'
            
            # Google News用の情報
            news = SubElement(url, 'news:news')
            publication = SubElement(news, 'news:publication')
            SubElement(publication, 'news:name').text = '日本のテックニュース速報'
            SubElement(publication, 'news:language').text = 'ja'
            
            news_article = SubElement(news, 'news:publication_date').text = last_mod
            SubElement(news, 'news:title').text = article.get('title', '')[:100]  # タイトルを100文字に制限
    
    # XMLを整形
    rough_string = tostring(urlset, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    # XMLファイルを保存
    with open('output/sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(pretty_xml.split('\n', 1)[1])  # XML宣言を除去して保存
    
    # ルートディレクトリにもコピー
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(pretty_xml.split('\n', 1)[1])
    
    print(f"✅ XML Sitemap generated:")
    print(f"  - Total pages: {site_data['total_pages']}")
    print(f"  - Total articles: {site_data['articles_count']}")
    print(f"  - Files: output/sitemap.xml, sitemap.xml")
    
    return True

if __name__ == "__main__":
    print("=== XML Sitemap Generator ===")
    generate_sitemap()