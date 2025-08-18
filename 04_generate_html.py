#!/usr/bin/env python3

import json
import os
from datetime import datetime
from jinja2 import Template, FileSystemLoader, Environment
from config import (
    AFFILIATE_ARTICLES_FILE, 
    FINAL_HTML_FILE, 
    OUTPUT_DIR,
    SITE_TITLE, 
    SITE_DESCRIPTION, 
    UPDATE_TIME,
    DEBUG, 
    VERBOSE
)

def load_template():
    """HTMLテンプレートを読み込み"""
    template_dir = "templates"
    template_file = "index.html"
    
    if not os.path.exists(os.path.join(template_dir, template_file)):
        print(f"Error: Template file not found: {template_dir}/{template_file}")
        return None
    
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    return template

def sort_articles(articles):
    """記事をソート（新しい順、重要度順）"""
    def sort_key(article):
        # 公開日時でソート（新しい順）
        published = article.get("published", "")
        try:
            # ISO形式の日時があれば使用
            if "T" in published:
                return published
            # なければ取得時刻を使用
            return article.get("fetched_at", "")
        except:
            return article.get("fetched_at", "")
    
    sorted_articles = sorted(articles, key=sort_key, reverse=True)
    
    if VERBOSE:
        print(f"Sorted {len(sorted_articles)} articles by publication date")
    
    return sorted_articles

def calculate_stats(data):
    """統計情報を計算"""
    articles = data.get("articles", [])
    
    stats = {
        "total_articles": len(articles),
        "total_affiliate_links": data.get("total_affiliate_links", 0),
        "total_feeds": len(set(article.get("source_name", "") for article in articles)),
        "categories": {},
        "platforms": {"amazon": 0, "rakuten": 0, "mixed": 0}
    }
    
    # カテゴリ統計
    for article in articles:
        category = article.get("category", "general")
        stats["categories"][category] = stats["categories"].get(category, 0) + 1
        
        # プラットフォーム統計
        platform = article.get("monetization", {}).get("primary_platform", "mixed")
        if platform in stats["platforms"]:
            stats["platforms"][platform] += 1
    
    return stats

def enhance_articles_for_display(articles):
    """表示用に記事データを強化"""
    enhanced = []
    
    for article in articles:
        enhanced_article = article.copy()
        
        # カテゴリの日本語化
        category_map = {
            "tech": "テクノロジー",
            "gadget": "ガジェット", 
            "book": "書籍",
            "business": "ビジネス",
            "general": "一般"
        }
        enhanced_article["category_jp"] = category_map.get(
            article.get("category", "general"), "一般"
        )
        
        # 要約の長さ調整（表示用）
        summary = article.get("summary", "")
        if len(summary) > 300:
            enhanced_article["summary"] = summary[:297] + "..."
        
        # 日付のフォーマット
        published = article.get("published", "")
        if published:
            try:
                # 簡単な日付フォーマット処理
                enhanced_article["published_formatted"] = published[:10]  # YYYY-MM-DD
            except:
                enhanced_article["published_formatted"] = "不明"
        else:
            enhanced_article["published_formatted"] = "不明"
        
        # アフィリエイトリンクの存在確認
        affiliate_links = article.get("affiliate_links", {})
        has_links = (
            len(affiliate_links.get("keyword_based", [])) > 0 or 
            len(affiliate_links.get("category_recommendations", [])) > 0
        )
        enhanced_article["has_affiliate_links"] = has_links
        
        enhanced.append(enhanced_article)
    
    return enhanced

def generate_sitemap(articles):
    """簡単なサイトマップ情報を生成（将来の拡張用）"""
    sitemap_data = {
        "generated_at": datetime.now().isoformat(),
        "total_pages": 1,  # 現在は1ページのみ
        "articles_count": len(articles),
        "last_updated": UPDATE_TIME
    }
    
    return sitemap_data

def main():
    """メイン処理"""
    print("=== HTML Generator ===")
    
    if not os.path.exists(AFFILIATE_ARTICLES_FILE):
        print(f"Error: {AFFILIATE_ARTICLES_FILE} not found. Run 03_add_affiliate.py first.")
        return
    
    # テンプレート読み込み
    template = load_template()
    if not template:
        return
    
    # アフィリエイト処理済みデータを読み込み
    with open(AFFILIATE_ARTICLES_FILE, 'r', encoding='utf-8') as f:
        affiliate_data = json.load(f)
    
    # データ処理
    articles = affiliate_data.get("articles", [])
    sorted_articles = sort_articles(articles)
    enhanced_articles = enhance_articles_for_display(sorted_articles)
    stats = calculate_stats(affiliate_data)
    
    if VERBOSE:
        print(f"Processing {len(enhanced_articles)} articles for HTML generation")
    
    # テンプレートに渡すデータを準備
    template_data = {
        "site_title": SITE_TITLE,
        "site_description": SITE_DESCRIPTION,
        "update_time": UPDATE_TIME,
        "articles": enhanced_articles,
        "total_articles": stats["total_articles"],
        "total_affiliate_links": stats["total_affiliate_links"],
        "total_feeds": stats["total_feeds"],
        "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # HTML生成
    try:
        html_content = template.render(**template_data)
        
        # 出力ディレクトリ作成
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # HTMLファイル保存
        with open(FINAL_HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n=== Summary ===")
        print(f"HTML generated successfully: {FINAL_HTML_FILE}")
        print(f"Total articles: {stats['total_articles']}")
        print(f"Total affiliate links: {stats['total_affiliate_links']}")
        print(f"Categories: {', '.join(stats['categories'].keys())}")
        
        if DEBUG:
            print(f"\nCategory breakdown:")
            for category, count in stats["categories"].items():
                print(f"  {category}: {count}")
            
            print(f"\nAffiliate platform breakdown:")
            for platform, count in stats["platforms"].items():
                print(f"  {platform}: {count}")
        
        # サイトマップ情報生成（将来の拡張用）
        sitemap = generate_sitemap(enhanced_articles)
        sitemap_file = os.path.join(OUTPUT_DIR, "sitemap.json")
        with open(sitemap_file, 'w', encoding='utf-8') as f:
            json.dump(sitemap, f, ensure_ascii=False, indent=2)
        
        if VERBOSE:
            print(f"Sitemap data saved: {sitemap_file}")
        
        # ファイルサイズ確認
        file_size = os.path.getsize(FINAL_HTML_FILE)
        print(f"Generated HTML size: {file_size:,} bytes")
        
        print(f"\n✅ Ready for GitHub Pages deployment!")
        
    except Exception as e:
        print(f"Error generating HTML: {e}")
        raise

if __name__ == "__main__":
    main()