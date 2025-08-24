#!/usr/bin/env python3

import json
import os
import urllib.parse
from datetime import datetime
from config import PROCESSED_ARTICLES_FILE, AFFILIATE_ARTICLES_FILE, AFFILIATE_CONFIGS, DEBUG, VERBOSE

def generate_amazon_search_link(keyword, config):
    """記事のキーワードに基づいてAmazon検索リンクを生成"""
    tag = config["tag"]
    encoded_keyword = urllib.parse.quote(keyword)
    
    affiliate_url = f"https://www.amazon.co.jp/s?k={encoded_keyword}&tag={tag}&linkCode=ur2&linkId=amazon_search"
    
    return {
        "platform": "amazon",
        "keyword": keyword,
        "url": affiliate_url,
        "title": f"{keyword} - Amazon検索結果",
        "display_text": f"🛒 {keyword}をAmazonで探す",
        "description": f"Amazonで{keyword}に関連する商品をチェック",
        "price": "価格を確認",
        "image_url": "https://m.media-amazon.com/images/G/09/associates/remote-buy-box/buy-now.png",
        "rating": None
    }

def get_relevant_keywords_for_affiliate(keywords, category, title=""):
    """記事に関連するアフィリエイトキーワードを抽出"""
    relevant_keywords = []
    title_lower = title.lower()
    
    # タイトルから直接的なキーワードを抽出
    title_keywords = []
    if "iphone" in title_lower or "アイフォン" in title_lower:
        title_keywords.extend(["iPhone", "スマートフォン", "アクセサリー"])
    elif "macbook" in title_lower or "マック" in title_lower:
        title_keywords.extend(["MacBook", "ノートPC", "アクセサリー"])  
    elif "ai" in title_lower or "人工知能" in title_lower or "機械学習" in title_lower:
        title_keywords.extend(["AI", "機械学習", "プログラミング"])
    elif "投資" in title_lower or "株価" in title_lower or "bitcoin" in title_lower:
        title_keywords.extend(["投資", "経済", "ビジネス"])
    elif "プログラミング" in title_lower or "開発" in title_lower:
        title_keywords.extend(["プログラミング", "開発", "技術書"])
    elif "playstation" in title_lower or "ps5" in title_lower or "ゲーム" in title_lower:
        title_keywords.extend(["ゲーム", "PlayStation", "ゲーミング"])
    
    # タイトルから抽出されたキーワードを最優先
    relevant_keywords.extend(title_keywords[:2])
    
    # 記事のキーワードから関連性の高いものを選択
    for keyword in keywords[:3]:
        if keyword not in relevant_keywords:
            relevant_keywords.append(keyword)
    
    # カテゴリベースのデフォルトキーワード
    category_defaults = {
        "AI・機械学習": ["AI", "機械学習"],
        "Apple製品": ["iPhone", "MacBook"],
        "プログラミング": ["プログラミング", "技術書"],
        "ゲーム": ["ゲーム", "PlayStation"],
        "ビジネス・経済": ["投資", "ビジネス"]
    }
    
    if category in category_defaults:
        for kw in category_defaults[category]:
            if kw not in relevant_keywords:
                relevant_keywords.append(kw)
    
    return relevant_keywords[:3]

def get_specific_product_database():
    """具体的な商品データベース（Amazon実物商品）"""
    return {
        # AI・機械学習関連
        "ai_programming": {
            "asin": "4295013773",
            "title": "ゼロから作るDeep Learning",
            "price": "￥4,180",
            "image": "https://m.media-amazon.com/images/I/81VYZdZbN7L._SX350_BO1,204,203,200_.jpg",
            "rating": "4.2"
        },
        "python_ml": {
            "asin": "4873119286",
            "title": "Python機械学習プログラミング",
            "price": "￥3,740",
            "image": "https://m.media-amazon.com/images/I/81rGdRHo-PL._SX350_BO1,204,203,200_.jpg",
            "rating": "4.1"
        },
        "chatgpt_book": {
            "asin": "4295018295",
            "title": "ChatGPT APIプログラミング 入門",
            "price": "￥2,860",
            "image": "https://m.media-amazon.com/images/I/81kf1mBnX1L._SX350_BO1,204,203,200_.jpg",
            "rating": "4.0"
        },
        
        # iPhoneアクセサリー
        "iphone_case": {
            "asin": "B0CX1WF4XY",
            "title": "Apple iPhone 15 Pro シリコンケース",
            "price": "￥6,800",
            "image": "https://m.media-amazon.com/images/I/61P9mVSO8sL._AC_SX679_.jpg",
            "rating": "4.4"
        },
        "magsafe_charger": {
            "asin": "B08P4CZYQX",
            "title": "Apple MagSafe充電器",
            "price": "￥5,930",
            "image": "https://m.media-amazon.com/images/I/61SUkK0DFQL._AC_SX679_.jpg",
            "rating": "4.3"
        },
        "lightning_cable": {
            "asin": "B075853FRF",
            "title": "Apple Lightning - USBケーブル (1 m)",
            "price": "￥2,668",
            "image": "https://m.media-amazon.com/images/I/31rAao-WFpL._AC_SX679_.jpg",
            "rating": "4.5"
        },
        
        # MacBookアクセサリー
        "macbook_case": {
            "asin": "B0BXJX3QBL",
            "title": "MacBook Pro 14インチ M3 ハードケース",
            "price": "￥2,980",
            "image": "https://m.media-amazon.com/images/I/71BhpHO4iYL._AC_SX679_.jpg",
            "rating": "4.2"
        },
        "usb_c_hub": {
            "asin": "B09C8QZQ8G",
            "title": "Anker PowerExpand 8-in-1 USB-C PD メディア ハブ",
            "price": "￥9,990",
            "image": "https://m.media-amazon.com/images/I/61YJkMtA-kL._AC_SX679_.jpg",
            "rating": "4.3"
        },
        "external_ssd": {
            "asin": "B084HPXZ5J",
            "title": "SanDisk ポータブルSSD 1TB",
            "price": "￥13,980",
            "image": "https://m.media-amazon.com/images/I/61Dr8R15tXL._AC_SX679_.jpg",
            "rating": "4.4"
        },
        
        # プログラミング書籍
        "clean_code": {
            "asin": "4048930591",
            "title": "リーダブルコード",
            "price": "￥2,640",
            "image": "https://m.media-amazon.com/images/I/51MgH8Jmr3L._SX350_BO1,204,203,200_.jpg",
            "rating": "4.2"
        },
        "javascript_book": {
            "asin": "4873119707",
            "title": "JavaScript: The Definitive Guide, 7th Edition",
            "price": "￥5,060",
            "image": "https://m.media-amazon.com/images/I/91MZCe9YuFL._SX350_BO1,204,203,200_.jpg",
            "rating": "4.1"
        },
        
        # ゲーミング
        "ps5_controller": {
            "asin": "B08H99BPJN",
            "title": "PlayStation 5 DualSense ワイヤレスコントローラー",
            "price": "￥8,778",
            "image": "https://m.media-amazon.com/images/I/51g0MEHbM9L._AC_SX679_.jpg",
            "rating": "4.5"
        },
        "gaming_headset": {
            "asin": "B07SQDVL8Z",
            "title": "SteelSeries Arctis 7P ワイヤレスゲーミングヘッドセット",
            "price": "￥16,182",
            "image": "https://m.media-amazon.com/images/I/71vKjlK5OcL._AC_SX679_.jpg",
            "rating": "4.4"
        },
        
        # 投資・ビジネス書
        "investment_book": {
            "asin": "4532358213",
            "title": "つみたてNISAの教科書 2024",
            "price": "￥1,595",
            "image": "https://m.media-amazon.com/images/I/81Xk1xHLHBL._SX350_BO1,204,203,200_.jpg",
            "rating": "4.3"
        },
        "startup_book": {
            "asin": "4822255018",
            "title": "リーンスタートアップ",
            "price": "￥2,420",
            "image": "https://m.media-amazon.com/images/I/814s1Z7fBNL._SX350_BO1,204,203,200_.jpg",
            "rating": "4.1"
        }
    }


def match_keywords_to_affiliates(keywords, category, title=""):
    """記事のキーワードに基づいて動的にアフィリエイトリンクを生成"""
    affiliate_links = []
    
    # 記事に関連するキーワードを取得
    relevant_keywords = get_relevant_keywords_for_affiliate(keywords, category, title)
    
    # カテゴリ別プラットフォーム戦略
    category_strategies = {
        "tech": ["amazon"],
        "AI・機械学習": ["amazon"],
        "Apple製品": ["amazon"],
        "ガジェット": ["amazon"],  
        "ビジネス・経済": ["amazon"],
        "ゲーム": ["amazon"],
        "書籍・教育": ["amazon"],
        "general": ["amazon"]
    }
    
    platforms = category_strategies.get(category, ["amazon"])
    
    # キーワードベースの検索リンク生成
    for keyword in relevant_keywords:
        if "amazon" in platforms:
            link = generate_amazon_search_link(keyword, AFFILIATE_CONFIGS["amazon"])
            if link:
                affiliate_links.append(link)
    
    return affiliate_links[:3]  # 最大3つの検索ベースアフィリエイトリンク

def generate_category_recommendations(category):
    """カテゴリに基づいた関連キーワード検索リンクを生成"""
    category_keyword_mapping = {
        "tech": ["技術", "テクノロジー"],
        "AI・機械学習": ["AI", "機械学習"],
        "Apple製品": ["iPhone", "MacBook"],
        "プログラミング": ["プログラミング", "技術書"],
        "ゲーム": ["ゲーム", "ゲーミング"],
        "ビジネス・経済": ["投資", "ビジネス"],
        "general": ["テクノロジー", "ガジェット"]
    }
    
    keywords = category_keyword_mapping.get(category, category_keyword_mapping["general"])
    affiliate_recs = []
    
    for keyword in keywords:
        link = generate_amazon_search_link(keyword, AFFILIATE_CONFIGS["amazon"])
        if link:
            affiliate_recs.append(link)
    
    return affiliate_recs[:2]  # カテゴリ推薦は最大2つ

def add_affiliate_links(article):
    """記事にアフィリエイトリンクを追加（改善版）"""
    enhanced_article = article.copy()
    enhanced_article["affiliate_processed_at"] = datetime.now().isoformat()
    
    keywords = article.get("keywords", [])
    category = article.get("category", "general")
    title = article.get("title", "")
    
    # キーワードベースのアフィリエイトリンク（タイトル分析を含む）
    keyword_links = match_keywords_to_affiliates(keywords, category, title)
    
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