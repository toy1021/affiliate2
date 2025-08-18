#!/usr/bin/env python3

import json
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from config import RSS_RAW_FILE, PROCESSED_ARTICLES_FILE, SUMMARY_LENGTH, DEBUG, VERBOSE

def clean_html(html_text):
    """HTMLタグを除去してクリーンなテキストを取得"""
    if not html_text:
        return ""
    
    soup = BeautifulSoup(html_text, 'html.parser')
    text = soup.get_text()
    
    # 複数の空白・改行を単一スペースに
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def create_summary(text, max_length=SUMMARY_LENGTH):
    """テキストから要約を作成（シンプルな切り詰め版）"""
    if not text:
        return ""
    
    # HTMLを除去
    clean_text = clean_html(text)
    
    # 長すぎる場合は切り詰め
    if len(clean_text) > max_length:
        # 単語の途中で切れないように調整
        truncated = clean_text[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:  # 80%以上の位置にスペースがあれば
            truncated = truncated[:last_space]
        truncated += "..."
        return truncated
    
    return clean_text

def extract_keywords(text):
    """テキストからキーワードを抽出（シンプルな実装）"""
    if not text:
        return []
    
    # 共通キーワード（アフィリエイト商品関連）
    tech_keywords = [
        "iPhone", "Android", "スマートフォン", "スマホ", "タブレット",
        "PC", "ノートパソコン", "MacBook", "iPad", "Surface",
        "カメラ", "ヘッドホン", "イヤホン", "スピーカー",
        "AI", "機械学習", "プログラミング", "本", "書籍",
        "ガジェット", "アプリ", "ソフトウェア", "ゲーム"
    ]
    
    found_keywords = []
    text_lower = text.lower()
    
    for keyword in tech_keywords:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords[:5]  # 最大5個

def categorize_article(title, content, keywords):
    """記事をカテゴリ分類"""
    combined_text = f"{title} {content}".lower()
    
    categories = {
        "tech": ["technology", "tech", "ai", "software", "app", "テクノロジー", "アプリ", "ソフト"],
        "gadget": ["device", "smartphone", "iphone", "android", "gadget", "スマホ", "ガジェット"],
        "book": ["book", "read", "author", "publish", "本", "書籍", "読書"],
        "business": ["business", "economy", "market", "company", "ビジネス", "経済"],
        "general": []
    }
    
    for category, category_keywords in categories.items():
        if category == "general":
            continue
        for keyword in category_keywords:
            if keyword in combined_text:
                return category
    
    return "general"

def process_article(article):
    """単一記事の処理"""
    processed = {
        "id": f"{article.get('source_name', 'unknown')}_{hash(article.get('link', '')) % 10000}",
        "title": article.get("title", ""),
        "original_link": article.get("link", ""),
        "source_name": article.get("source_name", ""),
        "source_feed": article.get("source_feed", ""),
        "published": article.get("published", ""),
        "fetched_at": article.get("fetched_at", ""),
        "processed_at": datetime.now().isoformat()
    }
    
    # コンテンツ処理
    description = article.get("description", "")
    summary = article.get("summary", "")
    content = description if len(description) > len(summary) else summary
    
    processed["original_content"] = content
    processed["clean_content"] = clean_html(content)
    processed["summary"] = create_summary(processed["clean_content"])
    processed["keywords"] = extract_keywords(f"{processed['title']} {processed['clean_content']}")
    processed["category"] = categorize_article(processed["title"], processed["clean_content"], processed["keywords"])
    processed["tags"] = article.get("tags", [])
    
    return processed

def main():
    """メイン処理"""
    print("=== Content Processor ===")
    
    if not os.path.exists(RSS_RAW_FILE):
        print(f"Error: {RSS_RAW_FILE} not found. Run 01_fetch_rss.py first.")
        return
    
    # RSS生データを読み込み
    with open(RSS_RAW_FILE, 'r', encoding='utf-8') as f:
        rss_data = json.load(f)
    
    processed_articles = []
    
    for feed in rss_data.get("feeds", []):
        if VERBOSE:
            print(f"Processing feed: {feed.get('feed_title', 'Unknown')}")
        
        for article in feed.get("articles", []):
            try:
                processed = process_article(article)
                processed_articles.append(processed)
                
                if DEBUG:
                    print(f"  - {processed['title'][:50]}...")
                    
            except Exception as e:
                print(f"Error processing article: {e}")
                continue
    
    # 結果を保存
    output_data = {
        "process_timestamp": datetime.now().isoformat(),
        "total_articles": len(processed_articles),
        "articles": processed_articles
    }
    
    with open(PROCESSED_ARTICLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Summary ===")
    print(f"Total articles processed: {len(processed_articles)}")
    print(f"Data saved to: {PROCESSED_ARTICLES_FILE}")
    
    # カテゴリ別統計
    categories = {}
    for article in processed_articles:
        cat = article.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nCategories:")
    for cat, count in categories.items():
        print(f"  {cat}: {count}")
    
    if DEBUG and processed_articles:
        print(f"\nSample processed article:")
        sample = processed_articles[0]
        print(f"Title: {sample['title']}")
        print(f"Category: {sample['category']}")
        print(f"Keywords: {', '.join(sample['keywords'])}")
        print(f"Summary: {sample['summary'][:100]}...")

if __name__ == "__main__":
    main()