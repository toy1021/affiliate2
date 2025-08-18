#!/usr/bin/env python3

import json
import os
import urllib.parse
from datetime import datetime
from config import PROCESSED_ARTICLES_FILE, AFFILIATE_ARTICLES_FILE, AFFILIATE_CONFIGS, DEBUG, VERBOSE

def generate_amazon_link(keyword, config):
    """Amazonアフィリエイトリンクを生成"""
    base_url = config["search_base_url"]
    tag = config["tag"]
    
    search_query = urllib.parse.quote(keyword)
    affiliate_url = f"{base_url}{search_query}&linkCode=ll2&tag={tag}&linkId=your-link-id"
    
    return {
        "platform": "amazon",
        "keyword": keyword,
        "url": affiliate_url,
        "display_text": f"{keyword}を検索 - Amazon"
    }

def generate_rakuten_link(keyword, config):
    """楽天アフィリエイトリンクを生成"""
    base_url = config["search_base_url"]
    affiliate_id = config["affiliate_id"]
    
    search_query = urllib.parse.quote(keyword)
    affiliate_url = f"{base_url}{search_query}/?f=1&grp=product"
    
    return {
        "platform": "rakuten",
        "keyword": keyword,
        "url": affiliate_url,
        "display_text": f"{keyword}を検索 - 楽天市場"
    }

def match_keywords_to_affiliates(keywords, category):
    """キーワードとカテゴリに基づいてアフィリエイトリンクを生成"""
    affiliate_links = []
    
    # カテゴリ別のアフィリエイト戦略
    category_strategies = {
        "tech": ["amazon", "rakuten"],
        "gadget": ["amazon", "rakuten"],  
        "book": ["amazon"],
        "business": ["amazon"],
        "general": ["amazon"]
    }
    
    platforms = category_strategies.get(category, ["amazon"])
    
    for keyword in keywords[:3]:  # 上位3つのキーワード
        for platform in platforms:
            if platform == "amazon" and any(k in keyword.lower() for k in AFFILIATE_CONFIGS["amazon"]["keywords"]):
                link = generate_amazon_link(keyword, AFFILIATE_CONFIGS["amazon"])
                affiliate_links.append(link)
                
            elif platform == "rakuten" and any(k in keyword for k in AFFILIATE_CONFIGS["rakuten"]["keywords"]):
                link = generate_rakuten_link(keyword, AFFILIATE_CONFIGS["rakuten"])
                affiliate_links.append(link)
    
    # キーワードがマッチしない場合は、カテゴリに基づいて汎用的なリンクを生成
    if not affiliate_links:
        if category == "tech":
            affiliate_links.append(generate_amazon_link("プログラミング本", AFFILIATE_CONFIGS["amazon"]))
        elif category == "gadget":
            affiliate_links.append(generate_amazon_link("スマホアクセサリー", AFFILIATE_CONFIGS["amazon"]))
        elif category == "book":
            affiliate_links.append(generate_amazon_link("ビジネス書", AFFILIATE_CONFIGS["amazon"]))
        else:
            affiliate_links.append(generate_amazon_link("おすすめ商品", AFFILIATE_CONFIGS["amazon"]))
    
    return affiliate_links[:2]  # 最大2つのアフィリエイトリンク

def generate_category_recommendations(category):
    """カテゴリに基づいた関連商品推薦を生成"""
    recommendations = {
        "tech": [
            {"text": "プログラミング学習におすすめ", "search": "プログラミング 入門書"},
            {"text": "開発効率を上げるツール", "search": "プログラマー ツール"}
        ],
        "gadget": [
            {"text": "最新ガジェットをチェック", "search": "最新 ガジェット"},
            {"text": "スマホアクセサリー", "search": "スマートフォン アクセサリー"}
        ],
        "book": [
            {"text": "関連書籍を探す", "search": "ビジネス書 ランキング"},
            {"text": "Kindle Unlimitedで読み放題", "search": "kindle unlimited"}
        ],
        "business": [
            {"text": "ビジネススキル向上に", "search": "ビジネス スキル 本"},
            {"text": "経営・マーケティング書籍", "search": "マーケティング 本"}
        ],
        "general": [
            {"text": "今週のおすすめ商品", "search": "おすすめ商品"},
            {"text": "人気ランキング", "search": "人気 ランキング"}
        ]
    }
    
    category_recs = recommendations.get(category, recommendations["general"])
    affiliate_recs = []
    
    for rec in category_recs:
        amazon_link = generate_amazon_link(rec["search"], AFFILIATE_CONFIGS["amazon"])
        amazon_link["display_text"] = rec["text"]
        affiliate_recs.append(amazon_link)
    
    return affiliate_recs

def add_affiliate_links(article):
    """記事にアフィリエイトリンクを追加"""
    enhanced_article = article.copy()
    enhanced_article["affiliate_processed_at"] = datetime.now().isoformat()
    
    keywords = article.get("keywords", [])
    category = article.get("category", "general")
    
    # キーワードベースのアフィリエイトリンク
    keyword_links = match_keywords_to_affiliates(keywords, category)
    
    # カテゴリベースの推薦
    category_recommendations = generate_category_recommendations(category)
    
    enhanced_article["affiliate_links"] = {
        "keyword_based": keyword_links,
        "category_recommendations": category_recommendations,
        "total_links": len(keyword_links) + len(category_recommendations)
    }
    
    # メタデータ
    enhanced_article["monetization"] = {
        "has_affiliate": len(keyword_links) > 0 or len(category_recommendations) > 0,
        "link_count": len(keyword_links) + len(category_recommendations),
        "primary_platform": "amazon" if any("amazon" in link.get("platform", "") for link in keyword_links) else "mixed"
    }
    
    return enhanced_article

def main():
    """メイン処理"""
    print("=== Affiliate Link Processor ===")
    
    if not os.path.exists(PROCESSED_ARTICLES_FILE):
        print(f"Error: {PROCESSED_ARTICLES_FILE} not found. Run 02_process_content.py first.")
        return
    
    # 処理済み記事データを読み込み
    with open(PROCESSED_ARTICLES_FILE, 'r', encoding='utf-8') as f:
        processed_data = json.load(f)
    
    articles_with_affiliate = []
    
    for article in processed_data.get("articles", []):
        if VERBOSE:
            print(f"Adding affiliate links to: {article.get('title', 'Unknown')[:50]}...")
        
        try:
            enhanced = add_affiliate_links(article)
            articles_with_affiliate.append(enhanced)
            
            if DEBUG:
                links = enhanced.get("affiliate_links", {})
                total_links = links.get("total_links", 0)
                print(f"  - Added {total_links} affiliate links")
                
        except Exception as e:
            print(f"Error adding affiliate links to article: {e}")
            articles_with_affiliate.append(article)  # 元記事を保持
    
    # 結果を保存
    output_data = {
        "affiliate_process_timestamp": datetime.now().isoformat(),
        "total_articles": len(articles_with_affiliate),
        "total_affiliate_links": sum(
            article.get("affiliate_links", {}).get("total_links", 0) 
            for article in articles_with_affiliate
        ),
        "articles": articles_with_affiliate
    }
    
    with open(AFFILIATE_ARTICLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Summary ===")
    print(f"Total articles processed: {len(articles_with_affiliate)}")
    print(f"Total affiliate links added: {output_data['total_affiliate_links']}")
    print(f"Data saved to: {AFFILIATE_ARTICLES_FILE}")
    
    # プラットフォーム別統計
    platform_stats = {"amazon": 0, "rakuten": 0, "mixed": 0}
    for article in articles_with_affiliate:
        platform = article.get("monetization", {}).get("primary_platform", "mixed")
        platform_stats[platform] = platform_stats.get(platform, 0) + 1
    
    print(f"\nAffiliate Platform Distribution:")
    for platform, count in platform_stats.items():
        print(f"  {platform}: {count}")
    
    if DEBUG and articles_with_affiliate:
        print(f"\nSample affiliate links:")
        sample = articles_with_affiliate[0]
        links = sample.get("affiliate_links", {})
        for link in links.get("keyword_based", [])[:2]:
            print(f"  - {link.get('display_text', 'Unknown')}")

if __name__ == "__main__":
    main()