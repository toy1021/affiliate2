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

def get_smart_product_recommendations(keywords, category):
    """キーワードとカテゴリに基づく高精度商品推薦"""
    
    # キーワード → 商品マッピング（より詳細）
    keyword_product_map = {
        # AI・プログラミング関連
        "AI": ["AI プログラミング 本", "Python 機械学習 本", "ChatGPT 活用法"],
        "ChatGPT": ["ChatGPT 本", "AI 活用 ガイドブック", "プロンプト エンジニアリング"],
        "Python": ["Python 入門書", "データ分析 本", "プログラミング 学習本"],
        "JavaScript": ["JavaScript 本", "Web開発 教本", "React 入門書"],
        "React": ["React 開発本", "フロントエンド 開発書", "JavaScript フレームワーク"],
        
        # Apple製品
        "iPhone": ["iPhone ケース", "iPhone 充電器", "iPhone アクセサリー", "ワイヤレス充電器"],
        "iPad": ["iPad ケース", "Apple Pencil", "iPad キーボード", "タブレット スタンド"],
        "MacBook": ["MacBook ケース", "USB-C ハブ", "外付けSSD", "ワイヤレスマウス"],
        "AirPods": ["AirPods ケース", "ワイヤレスイヤホン", "イヤホン 収納"],
        
        # Android・Google
        "Android": ["Android ケース", "Android 充電器", "スマホ アクセサリー"],
        "Pixel": ["Pixel ケース", "Google Pixel アクセサリー", "Android 本"],
        
        # ガジェット
        "ヘッドホン": ["ノイズキャンセリング ヘッドホン", "ワイヤレス ヘッドホン", "ゲーミング ヘッドセット"],
        "カメラ": ["ミラーレス カメラ", "カメラ レンズ", "三脚", "カメラ ストラップ"],
        "スマートウォッチ": ["Apple Watch バンド", "スマートウォッチ 充電器", "フィットネス トラッカー"],
        
        # ビジネス・投資
        "投資": ["投資 入門書", "株式投資 本", "資産運用 ガイド"],
        "スタートアップ": ["起業 本", "ビジネス書", "経営戦略 本"],
        "Bitcoin": ["仮想通貨 本", "ブロックチェーン 解説書", "投資 ガイド"],
        
        # 自動車
        "Tesla": ["電気自動車 本", "Tesla グッズ", "EV 充電器"],
        "電気自動車": ["EV 充電ケーブル", "電気自動車 本", "カー アクセサリー"],
        
        # ゲーム
        "PlayStation": ["PS5 アクセサリー", "ゲーミング ヘッドセット", "コントローラー"],
        "Nintendo Switch": ["Switch ケース", "Pro コントローラー", "ゲームソフト"],
        "Steam": ["ゲーミング キーボード", "ゲーミング マウス", "PC ゲーム"]
    }
    
    recommended_products = []
    
    # キーワードベースの推薦
    for keyword in keywords[:5]:
        if keyword in keyword_product_map:
            products = keyword_product_map[keyword][:2]  # 各キーワードから最大2商品
            recommended_products.extend(products)
    
    # カテゴリベースの追加推薦
    category_defaults = {
        "tech": ["プログラミング 本", "開発者 ツール"],
        "AI・機械学習": ["AI 入門書", "機械学習 実践書"],
        "Apple製品": ["Apple アクセサリー", "iPhone グッズ"],
        "ガジェット": ["最新 ガジェット", "スマホ アクセサリー"],
        "ビジネス": ["ビジネス書 ランキング", "自己啓発 本"],
        "ゲーム": ["ゲーミング デバイス", "ゲーム グッズ"],
        "general": ["人気商品 ランキング", "おすすめ グッズ"]
    }
    
    if category in category_defaults:
        recommended_products.extend(category_defaults[category])
    
    # 重複除去と優先度調整
    unique_products = list(dict.fromkeys(recommended_products))
    
    return unique_products[:4]  # 最大4つの商品推薦

def match_keywords_to_affiliates(keywords, category):
    """高精度アフィリエイトリンク生成"""
    affiliate_links = []
    
    # 商品推薦を取得
    recommended_products = get_smart_product_recommendations(keywords, category)
    
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
    
    # 推薦商品からアフィリエイトリンク生成
    for product in recommended_products:
        for platform in platforms[:2]:  # 最大2プラットフォーム
            if platform == "amazon":
                link = generate_amazon_link(product, AFFILIATE_CONFIGS["amazon"])
                link["display_text"] = f"🛒 {product}"
                affiliate_links.append(link)
                break  # 同じ商品で複数プラットフォームは避ける
            elif platform == "rakuten":
                link = generate_rakuten_link(product, AFFILIATE_CONFIGS["rakuten"])
                link["display_text"] = f"🛒 {product}"
                affiliate_links.append(link)
                break
    
    return affiliate_links[:3]  # 最大3つのアフィリエイトリンク

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