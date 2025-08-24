#!/usr/bin/env python3

import json
import os
import urllib.parse
from datetime import datetime
from config import PROCESSED_ARTICLES_FILE, AFFILIATE_ARTICLES_FILE, AFFILIATE_CONFIGS, DEBUG, VERBOSE

def generate_specific_amazon_link(product_key, config):
    """Amazon実物商品への直接アフィリエイトリンクを生成"""
    products_db = get_specific_product_database()
    tag = config["tag"]
    
    if product_key not in products_db:
        return None
    
    product = products_db[product_key]
    affiliate_url = f"https://www.amazon.co.jp/dp/{product['asin']}?tag={tag}&linkCode=osi&th=1&psc=1"
    
    return {
        "platform": "amazon",
        "asin": product["asin"],
        "url": affiliate_url,
        "title": product["title"],
        "display_text": f"🛒 {product['title']}",
        "description": f"Amazonで{product['title']}をチェック",
        "price": product["price"],
        "image_url": product["image"],
        "rating": product["rating"]
    }

def generate_rakuten_link(product_key, config):
    """楽天アフィリエイトリンクを生成（具体的商品用）"""
    products_db = get_specific_product_database()
    affiliate_id = config.get("affiliate_id", "")
    
    if product_key not in products_db:
        return None
    
    product = products_db[product_key]
    # 楽天では検索ベースのリンクを使用
    search_query = urllib.parse.quote(product["title"])
    affiliate_url = f"https://search.rakuten.co.jp/search/mall/{search_query}/?f=1&grp=product"
    
    return {
        "platform": "rakuten", 
        "keyword": product["title"],
        "url": affiliate_url,
        "title": product["title"],
        "display_text": f"🛒 {product['title']}",
        "description": f"楽天で{product['title']}をチェック",
        "price": product.get("price", "価格を確認"),
        "image_url": product.get("image"),
        "rating": product.get("rating")
    }

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

def get_smart_product_recommendations(keywords, category, title=""):
    """キーワードとカテゴリに基づく高精度商品推薦（具体的商品）"""
    
    products_db = get_specific_product_database()
    title_lower = title.lower()
    recommended_product_keys = []
    
    # 記事タイトル分析による動的商品推薦
    if "iphone" in title_lower or "アイフォン" in title_lower:
        recommended_product_keys.extend(["iphone_case", "magsafe_charger", "lightning_cable"])
    elif "macbook" in title_lower or "マック" in title_lower:
        recommended_product_keys.extend(["macbook_case", "usb_c_hub", "external_ssd"])
    elif "ai" in title_lower or "人工知能" in title_lower or "機械学習" in title_lower:
        recommended_product_keys.extend(["ai_programming", "python_ml", "chatgpt_book"])
    elif "投資" in title_lower or "株価" in title_lower or "bitcoin" in title_lower:
        recommended_product_keys.extend(["investment_book", "startup_book"])
    elif "プログラミング" in title_lower or "開発" in title_lower:
        recommended_product_keys.extend(["clean_code", "javascript_book", "python_ml"])
    elif "playstation" in title_lower or "ps5" in title_lower or "ゲーム" in title_lower:
        recommended_product_keys.extend(["ps5_controller", "gaming_headset"])
    
    # キーワードベースの推薦（具体的商品キー）
    keyword_product_map = {
        "AI": ["ai_programming", "python_ml", "chatgpt_book"],
        "ChatGPT": ["chatgpt_book", "ai_programming", "python_ml"],
        "Python": ["python_ml", "clean_code", "javascript_book"],
        "JavaScript": ["javascript_book", "clean_code", "python_ml"],
        "React": ["javascript_book", "clean_code"],
        "iPhone": ["iphone_case", "magsafe_charger", "lightning_cable"],
        "MacBook": ["macbook_case", "usb_c_hub", "external_ssd"],
        "投資": ["investment_book", "startup_book"],
        "PlayStation": ["ps5_controller", "gaming_headset"],
        "プログラミング": ["clean_code", "python_ml", "javascript_book"]
    }
    
    recommended_products = []
    
    # キーワードベースの推薦を追加
    for keyword in keywords[:3]:
        if keyword in keyword_product_map:
            product_keys = keyword_product_map[keyword][:2]
            recommended_product_keys.extend(product_keys)
    
    # カテゴリベースのデフォルト推薦
    category_defaults = {
        "AI・機械学習": ["ai_programming", "python_ml"],
        "Apple製品": ["iphone_case", "magsafe_charger"],
        "プログラミング": ["clean_code", "python_ml"],
        "ゲーム": ["ps5_controller", "gaming_headset"],
        "ビジネス": ["investment_book", "startup_book"],
        "general": ["clean_code", "investment_book"]
    }
    
    if category in category_defaults:
        recommended_product_keys.extend(category_defaults[category])
    
    # 重複除去と優先度調整
    seen = set()
    unique_product_keys = []
    for key in recommended_product_keys:
        if key not in seen and key in products_db:
            unique_product_keys.append(key)
            seen.add(key)
    
    # 具体的商品情報を返す
    return unique_product_keys[:4]

def match_keywords_to_affiliates(keywords, category, title=""):
    """高精度アフィリエイトリンク生成（記事タイトル分析を含む）"""
    affiliate_links = []
    
    # 商品推薦を取得（タイトル情報を含む）
    recommended_products = get_smart_product_recommendations(keywords, category, title)
    
    # カテゴリ別プラットフォーム戦略
    category_strategies = {
        "tech": ["amazon", "rakuten"],
        "AI・機械学習": ["amazon"],
        "Apple製品": ["amazon", "rakuten"],
        "ガジェット": ["amazon", "rakuten"],  
        "ビジネス": ["amazon"],
        "ゲーム": ["amazon", "rakuten"],
        "書籍・教育": ["amazon"],
        "general": ["amazon"]
    }
    
    platforms = category_strategies.get(category, ["amazon"])
    
    # 具体的商品からアフィリエイトリンク生成
    for product_key in recommended_products:
        if "amazon" in platforms:
            link = generate_specific_amazon_link(product_key, AFFILIATE_CONFIGS["amazon"])
            if link:
                affiliate_links.append(link)
    
    return affiliate_links[:4]  # 最大4つの具体的商品アフィリエイトリンク

def generate_category_recommendations(category):
    """カテゴリに基づいた関連商品推薦を生成（具体的商品）"""
    products_db = get_specific_product_database()
    
    category_product_mapping = {
        "tech": ["clean_code", "python_ml"],
        "AI・機械学習": ["ai_programming", "chatgpt_book"],
        "Apple製品": ["iphone_case", "magsafe_charger"],
        "プログラミング": ["javascript_book", "clean_code"],
        "ゲーム": ["ps5_controller", "gaming_headset"],
        "ビジネス": ["investment_book", "startup_book"],
        "general": ["clean_code", "investment_book"]
    }
    
    product_keys = category_product_mapping.get(category, category_product_mapping["general"])
    affiliate_recs = []
    
    for product_key in product_keys:
        if product_key in products_db:
            link = generate_specific_amazon_link(product_key, AFFILIATE_CONFIGS["amazon"])
            if link:
                link["display_text"] = f"🛒 {products_db[product_key]['title']}"
                affiliate_recs.append(link)
    
    return affiliate_recs

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