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
    ARTICLES_PER_PAGE,
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

def calculate_article_importance(article):
    """記事の重要度を計算"""
    importance_score = 0
    
    # キーワードベースの重要度
    high_priority_keywords = ["AI", "ChatGPT", "iPhone", "Tesla", "Bitcoin", "IPO", "買収", "新機能"]
    keywords = article.get("keywords", [])
    
    for keyword in keywords:
        if keyword in high_priority_keywords:
            importance_score += 3
        else:
            importance_score += 1
    
    # カテゴリベースの重要度
    category_weights = {
        "AI・機械学習": 10,
        "Apple製品": 8,
        "Google・Android": 7,
        "ビジネス・投資": 6,
        "テクノロジー": 5,
        "ガジェット": 4,
        "プログラミング": 4,
        "ゲーム": 3,
        "自動車・EV": 6,
        "暗号通貨・ブロックチェーン": 5
    }
    
    category = article.get("category", "")
    importance_score += category_weights.get(category, 2)
    
    # タイトルに重要キーワードがある場合
    title = article.get("title", "").lower()
    if any(word in title for word in ["新機能", "発表", "リリース", "画期的", "世界初"]):
        importance_score += 5
    
    # アフィリエイトリンク数による調整
    affiliate_links = article.get("affiliate_links", {})
    importance_score += affiliate_links.get("total_links", 0)
    
    return importance_score

def sort_articles(articles):
    """記事を重要度と新しさでソート"""
    def sort_key(article):
        # 重要度スコア（主要基準）
        importance = calculate_article_importance(article)
        
        # 公開日時（副次基準）
        published = article.get("published", "")
        fetched = article.get("fetched_at", "")
        
        # タイムスタンプの正規化
        try:
            if "T" in published:
                time_score = published
            elif fetched:
                time_score = fetched
            else:
                time_score = "1970-01-01T00:00:00"
        except:
            time_score = "1970-01-01T00:00:00"
        
        # 重要度を主要基準、時刻を副次基準とする複合キー
        return (importance, time_score)
    
    sorted_articles = sorted(articles, key=sort_key, reverse=True)
    
    if VERBOSE:
        print(f"Sorted {len(sorted_articles)} articles by importance and recency")
        # トップ5記事の重要度を表示
        for i, article in enumerate(sorted_articles[:5]):
            importance = calculate_article_importance(article)
            print(f"  #{i+1}: {article.get('title', 'Unknown')[:50]}... (Score: {importance})")
    
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

def paginate_articles(articles, page=1):
    """記事をページネーション"""
    total_articles = len(articles)
    total_pages = (total_articles + ARTICLES_PER_PAGE - 1) // ARTICLES_PER_PAGE
    
    start_index = (page - 1) * ARTICLES_PER_PAGE
    end_index = start_index + ARTICLES_PER_PAGE
    
    page_articles = articles[start_index:end_index]
    
    pagination_info = {
        "current_page": page,
        "total_pages": total_pages,
        "total_articles": total_articles,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_page": page - 1 if page > 1 else None,
        "next_page": page + 1 if page < total_pages else None,
        "articles_per_page": ARTICLES_PER_PAGE
    }
    
    return page_articles, pagination_info

def generate_sitemap(articles, total_pages=1):
    """簡単なサイトマップ情報を生成（将来の拡張用）"""
    sitemap_data = {
        "generated_at": datetime.now().isoformat(),
        "total_pages": total_pages,
        "articles_count": len(articles),
        "last_updated": UPDATE_TIME
    }
    
    return sitemap_data

def generate_multiple_pages(enhanced_articles, stats, template):
    """複数ページを生成"""
    total_articles = len(enhanced_articles)
    total_pages = (total_articles + ARTICLES_PER_PAGE - 1) // ARTICLES_PER_PAGE
    
    generated_files = []
    
    for page_num in range(1, total_pages + 1):
        # ページネーション
        page_articles, pagination_info = paginate_articles(enhanced_articles, page_num)
        
        # テンプレートに渡すデータを準備
        template_data = {
            "site_title": SITE_TITLE,
            "site_description": SITE_DESCRIPTION,
            "update_time": UPDATE_TIME,
            "articles": page_articles,
            "pagination": pagination_info,
            "total_articles": stats["total_articles"],
            "total_affiliate_links": stats["total_affiliate_links"],
            "total_feeds": stats["total_feeds"],
            "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # HTML生成
        html_content = template.render(**template_data)
        
        # ファイル名決定
        if page_num == 1:
            output_file = FINAL_HTML_FILE
        else:
            output_file = os.path.join(OUTPUT_DIR, f"page{page_num}.html")
        
        # HTMLファイル保存
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        generated_files.append(output_file)
        
        if VERBOSE:
            print(f"Generated page {page_num}/{total_pages}: {output_file}")
    
    return generated_files, total_pages

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
    
    # 出力ディレクトリ作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 複数ページ生成
    try:
        generated_files, total_pages = generate_multiple_pages(enhanced_articles, stats, template)
        
        print(f"\n=== Summary ===")
        print(f"HTML pages generated: {len(generated_files)}")
        print(f"Total articles: {stats['total_articles']}")
        print(f"Articles per page: {ARTICLES_PER_PAGE}")
        print(f"Total pages: {total_pages}")
        print(f"Total affiliate links: {stats['total_affiliate_links']}")
        print(f"Categories: {', '.join(stats['categories'].keys())}")
        
        if DEBUG:
            print(f"\nGenerated files:")
            for file_path in generated_files:
                print(f"  {file_path}")
            
            print(f"\nCategory breakdown:")
            for category, count in stats["categories"].items():
                print(f"  {category}: {count}")
            
            print(f"\nAffiliate platform breakdown:")
            for platform, count in stats["platforms"].items():
                print(f"  {platform}: {count}")
        
        # サイトマップ情報生成
        sitemap = generate_sitemap(enhanced_articles, total_pages)
        sitemap_file = os.path.join(OUTPUT_DIR, "sitemap.json")
        with open(sitemap_file, 'w', encoding='utf-8') as f:
            json.dump(sitemap, f, ensure_ascii=False, indent=2)
        
        if VERBOSE:
            print(f"Sitemap data saved: {sitemap_file}")
        
        # ファイルサイズ確認
        main_file_size = os.path.getsize(FINAL_HTML_FILE)
        print(f"Main page size: {main_file_size:,} bytes")
        
        print(f"\n✅ Ready for GitHub Pages deployment!")
        
    except Exception as e:
        print(f"Error generating HTML: {e}")
        raise

if __name__ == "__main__":
    main()