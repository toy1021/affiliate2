#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime, timedelta, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import hashlib

def generate_main_sitemap():
    """メインサイトマップを生成"""
    
    # サイト情報を読み込み
    if os.path.exists('output/sitemap.json'):
        with open('output/sitemap.json', 'r', encoding='utf-8') as f:
            site_data = json.load(f)
    else:
        print("Error: sitemap.json not found")
        return False
    
    # XML要素を作成
    urlset = Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
    
    base_url = 'https://toy1021.github.io/affiliate2/'
    jst = timezone(timedelta(hours=9))
    last_mod = datetime.now(jst).strftime('%Y-%m-%dT%H:%M:%S+09:00')
    
    # トップページ
    url = SubElement(urlset, 'url')
    SubElement(url, 'loc').text = base_url
    SubElement(url, 'lastmod').text = last_mod
    SubElement(url, 'changefreq').text = 'hourly'
    SubElement(url, 'priority').text = '1.0'
    
    # カテゴリページ（仮想URL）
    categories = ["AI・機械学習", "Apple製品", "プログラミング", "テクノロジー", "Google・Android"]
    for category in categories:
        url = SubElement(urlset, 'url')
        category_slug = hashlib.md5(category.encode('utf-8')).hexdigest()[:8]
        SubElement(url, 'loc').text = f"{base_url}#category-{category_slug}"
        SubElement(url, 'lastmod').text = last_mod
        SubElement(url, 'changefreq').text = 'daily'
        SubElement(url, 'priority').text = '0.9'
    
    # ページネーション
    for page_num in range(1, site_data['total_pages'] + 1):
        url = SubElement(urlset, 'url')
        if page_num == 1:
            SubElement(url, 'loc').text = base_url
        else:
            SubElement(url, 'loc').text = f"{base_url}#page-{page_num}"
        SubElement(url, 'lastmod').text = last_mod
        SubElement(url, 'changefreq').text = 'daily'
        SubElement(url, 'priority').text = '0.8' if page_num <= 3 else '0.6'
    
    # XMLを整形して保存
    save_xml(urlset, 'output/sitemap.xml', 'sitemap.xml')
    
    print(f"✅ Main Sitemap generated:")
    print(f"  - Total pages: {site_data['total_pages']}")
    print(f"  - Categories: {len(categories)}")
    
    return True

def generate_news_sitemap():
    """Google News用サイトマップを生成"""
    
    # 記事データを読み込み
    if not os.path.exists('output/articles.json'):
        print("Error: articles.json not found")
        return False
        
    with open('output/articles.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 最新48時間以内の記事のみを含める（Google Newsの要件）
    jst = timezone(timedelta(hours=9))
    cutoff_time = datetime.now(jst) - timedelta(hours=48)
    
    urlset = Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:news', 'http://www.google.com/schemas/sitemap-news/0.9')
    
    articles_added = 0
    
    # 全記事をチェック
    for page in data.get('pages', []):
        for article in page.get('articles', []):
            # 記事の公開日をチェック
            try:
                pub_date_str = article.get('pubDate', '')
                if pub_date_str:
                    # 記事の公開日をパース（簡単なフォーマットを想定）
                    article_date = datetime.strptime(pub_date_str[:19], '%Y-%m-%d %H:%M:%S')
                    article_date = article_date.replace(tzinfo=jst)
                    
                    # 48時間以内の記事のみ追加
                    if article_date > cutoff_time and articles_added < 100:  # 最大100記事
                        url = SubElement(urlset, 'url')
                        SubElement(url, 'loc').text = article.get('link', '')
                        SubElement(url, 'lastmod').text = article_date.strftime('%Y-%m-%dT%H:%M:%S+09:00')
                        
                        # Google News要素
                        news = SubElement(url, 'news:news')
                        publication = SubElement(news, 'news:publication')
                        SubElement(publication, 'news:name').text = '日本のテックニュース速報'
                        SubElement(publication, 'news:language').text = 'ja'
                        
                        SubElement(news, 'news:publication_date').text = article_date.strftime('%Y-%m-%dT%H:%M:%S+09:00')
                        SubElement(news, 'news:title').text = article.get('title', '')[:100]
                        
                        # ジャンル/キーワードを追加
                        keywords = article.get('category', 'テクノロジー')
                        SubElement(news, 'news:keywords').text = keywords
                        
                        articles_added += 1
            except:
                continue
    
    # XMLを保存
    save_xml(urlset, 'output/news_sitemap.xml', 'news_sitemap.xml')
    
    print(f"✅ News Sitemap generated:")
    print(f"  - Recent articles: {articles_added}")
    
    return True

def generate_sitemap_index():
    """サイトマップインデックスを生成"""
    
    sitemapindex = Element('sitemapindex')
    sitemapindex.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    base_url = 'https://toy1021.github.io/affiliate2/'
    jst = timezone(timedelta(hours=9))
    last_mod = datetime.now(jst).strftime('%Y-%m-%dT%H:%M:%S+09:00')
    
    # メインサイトマップ
    sitemap = SubElement(sitemapindex, 'sitemap')
    SubElement(sitemap, 'loc').text = f"{base_url}sitemap.xml"
    SubElement(sitemap, 'lastmod').text = last_mod
    
    # ニュースサイトマップ
    sitemap = SubElement(sitemapindex, 'sitemap')
    SubElement(sitemap, 'loc').text = f"{base_url}news_sitemap.xml"
    SubElement(sitemap, 'lastmod').text = last_mod
    
    # XMLを保存
    save_xml(sitemapindex, 'output/sitemap_index.xml', 'sitemap_index.xml')
    
    print(f"✅ Sitemap Index generated")
    
    return True

def save_xml(element, output_path, root_path):
    """XMLを整形して保存"""
    rough_string = tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    # XML宣言を含む完全なXMLとして保存
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    
    # ルートディレクトリにもコピー
    with open(root_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

def generate_sitemap():
    """全サイトマップを生成"""
    print("=== Enhanced Sitemap Generator ===")
    
    success = True
    success &= generate_main_sitemap()
    success &= generate_news_sitemap()
    success &= generate_sitemap_index()
    
    if success:
        print("\n🎉 All sitemaps generated successfully!")
        print("  - sitemap.xml (main)")
        print("  - news_sitemap.xml (Google News)")
        print("  - sitemap_index.xml (index)")
    
    return success

if __name__ == "__main__":
    print("=== XML Sitemap Generator ===")
    generate_sitemap()