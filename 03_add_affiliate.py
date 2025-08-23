#!/usr/bin/env python3

import json
import os
import urllib.parse
from datetime import datetime
from config import PROCESSED_ARTICLES_FILE, AFFILIATE_ARTICLES_FILE, AFFILIATE_CONFIGS, DEBUG, VERBOSE

def generate_amazon_link(keyword, config):
    """Amazonアフィリエイトリンクを生成（商品情報を強化）"""
    base_url = config["search_base_url"]
    tag = config["tag"]
    
    search_query = urllib.parse.quote(keyword)
    affiliate_url = f"{base_url}{search_query}&linkCode=ll2&tag={tag}&linkId=your-link-id"
    
    # 商品タイトルを最適化
    optimized_title = keyword.replace(" ", "・")
    
    return {
        "platform": "amazon",
        "keyword": keyword,
        "url": affiliate_url,
        "title": optimized_title,
        "display_text": f"🛒 {optimized_title}",
        "description": f"Amazonで{optimized_title}をチェック",
        "price": "価格を確認",
        "image_url": None  # Amazon商品画像は後で実装可能
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

def get_smart_product_recommendations(keywords, category, title=""):
    """キーワードとカテゴリに基づく高精度商品推薦（タイトル分析を追加）"""
    
    # 記事タイトル分析による動的商品推薦
    title_lower = title.lower()
    dynamic_recommendations = []
    
    # タイトル分析による商品推薦
    if "iphone" in title_lower or "アイフォン" in title_lower:
        dynamic_recommendations.extend(["iPhone ケース", "iPhone 充電器", "MagSafe 対応 アクセサリー"])
    elif "macbook" in title_lower or "マック" in title_lower:
        dynamic_recommendations.extend(["MacBook ケース", "USB-C ハブ", "外付けSSD"])
    elif "tesla" in title_lower or "テスラ" in title_lower:
        dynamic_recommendations.extend(["電気自動車 本", "Tesla グッズ", "EV 充電器"])
    elif "ai" in title_lower or "人工知能" in title_lower or "機械学習" in title_lower:
        dynamic_recommendations.extend(["AI プログラミング 本", "Python 機械学習 実践", "深層学習 教科書"])
    elif "投資" in title_lower or "株価" in title_lower or "bitcoin" in title_lower:
        dynamic_recommendations.extend(["投資 入門書", "株式投資 ガイド", "仮想通貨 解説書"])
    elif "プログラミング" in title_lower or "開発" in title_lower:
        dynamic_recommendations.extend(["プログラミング 本", "コーディング 学習書", "技術書 おすすめ"])
    
    # キーワード → 商品マッピング（改善版）
    keyword_product_map = {
        # AI・プログラミング関連（より具体的）
        "AI": ["AI プログラミング 実践", "機械学習 入門書", "ChatGPT 活用術"],
        "ChatGPT": ["生成AI 活用本", "プロンプトエンジニアリング", "AI ツール 解説書"],
        "Python": ["Python データ分析", "Python Web開発", "Python 自動化"],
        "JavaScript": ["JavaScript 完全ガイド", "Node.js 開発本", "フロントエンド 技術書"],
        "React": ["React 実践開発", "モダンフロントエンド", "JavaScript フレームワーク"],
        
        # Apple製品（モデル別）
        "iPhone": ["iPhone 15 ケース", "MagSafe 充電器", "Lightning ケーブル"],
        "iPad": ["iPad Pro ケース", "Apple Pencil 第2世代", "iPad キーボード"],
        "MacBook": ["MacBook Pro ケース", "Thunderbolt ハブ", "外付けSSD 1TB"],
        "Apple Watch": ["Apple Watch バンド", "ワイヤレス充電器", "スマートウォッチ アクセサリー"],
        
        # 最新ガジェット
        "VR": ["VR ヘッドセット", "Meta Quest", "VR ゲーム"],
        "ヘッドホン": ["Sony WH-1000XM5", "AirPods Pro", "ノイズキャンセリング"],
        "カメラ": ["ミラーレス一眼", "Canon EOS R", "Sony α7"],
        "スマートホーム": ["スマートスピーカー", "IoT デバイス", "ホームオートメーション"],
        
        # ビジネス・投資（トレンド重視）
        "投資": ["NISA 投資術", "インデックス投資", "資産運用 最新版"],
        "仮想通貨": ["暗号資産 入門", "ブロックチェーン技術", "DeFi 解説書"],
        "スタートアップ": ["起業 成功法則", "ビジネスモデル設計", "VC 資金調達"],
        
        # 自動車・モビリティ
        "Tesla": ["電気自動車 完全ガイド", "Tesla 関連書籍", "EV 充電設備"],
        "自動運転": ["自動運転技術 解説", "モビリティ革命", "AI 自動車"],
        
        # エンターテイメント
        "PlayStation": ["PS5 コントローラー", "ゲーミングヘッドセット", "4K ゲーミングモニター"],
        "Nintendo": ["Switch Proコントローラー", "Nintendo Switch ケース", "マリオ関連グッズ"],
        "ゲーム開発": ["Unity ゲーム開発", "Unreal Engine 5", "ゲームプログラミング"]
    }
    
    recommended_products = []
    
    # 動的推薦を優先
    recommended_products = dynamic_recommendations[:3]
    
    # キーワードベースの推薦（関連性を重視）
    for keyword in keywords[:3]:  # より厳選
        if keyword in keyword_product_map:
            products = keyword_product_map[keyword][:2]  # 各キーワードから2商品
            recommended_products.extend(products)
    
    # カテゴリベースの高品質推薦
    category_premium_products = {
        "tech": ["プログラミング必読書", "開発効率化ツール", "技術トレンド本 2025"],
        "AI・機械学習": ["機械学習 実装ガイド", "深層学習 PyTorch", "AI エンジニア必携"],
        "Apple製品": ["Apple 純正アクセサリー", "MagSafe対応製品", "Apple認定アクセサリー"],
        "ガジェット": ["2025年 注目ガジェット", "スマートデバイス", "未来テクノロジー"],
        "ビジネス": ["ビジネス書ベストセラー", "経営戦略 実践書", "リーダーシップ論"],
        "ゲーム": ["ゲーミングPC周辺機器", "eスポーツ デバイス", "VRゲーム機器"],
        "投資・金融": ["資産形成 完全ガイド", "投資信託 選び方", "節税対策 最新版"],
        "自動車": ["EV 充電アクセサリー", "カーエレクトロニクス", "自動運転技術書"],
        "general": ["Amazon売れ筋ランキング", "今週の注目商品", "レビュー高評価商品"]
    }
    
    if category in category_premium_products:
        recommended_products.extend(category_premium_products[category][:2])
    
    # 重複除去と優先度調整（動的推薦を最優先）
    seen = set()
    unique_products = []
    for product in recommended_products:
        if product not in seen:
            unique_products.append(product)
            seen.add(product)
    
    return unique_products[:5]  # 最大5つの商品推薦（品質重視）

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
    
    # 推薦商品からアフィリエイトリンク生成（品質向上）
    for product in recommended_products:
        for platform in platforms[:1]:  # Amazonに特化（品質重視）
            if platform == "amazon":
                link = generate_amazon_link(product, AFFILIATE_CONFIGS["amazon"])
                affiliate_links.append(link)
                break  # 同じ商品で複数プラットフォームは避ける
            elif platform == "rakuten":
                link = generate_rakuten_link(product, AFFILIATE_CONFIGS["rakuten"])
                affiliate_links.append(link)
                break
    
    return affiliate_links[:4]  # 最大4つのアフィリエイトリンク（品質重視）

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