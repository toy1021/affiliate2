#!/usr/bin/env python3

import json
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from config import RSS_RAW_FILE, PROCESSED_ARTICLES_FILE, SUMMARY_LENGTH, DEBUG, VERBOSE

def is_japanese_text(text):
    """日本語テキストかどうかを判定"""
    if not text:
        return False
    
    # ひらがな、カタカナ、漢字の正規表現
    japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
    japanese_chars = len(japanese_pattern.findall(text))
    total_chars = len(re.sub(r'\s+', '', text))
    
    # 全体の30%以上が日本語文字なら日本語テキストと判定
    if total_chars > 0:
        japanese_ratio = japanese_chars / total_chars
        return japanese_ratio >= 0.3
    
    return False

def clean_html(html_text):
    """HTMLタグを除去してクリーンなテキストを取得"""
    if not html_text:
        return ""
    
    soup = BeautifulSoup(html_text, 'html.parser')
    text = soup.get_text()
    
    # 複数の空白・改行を単一スペースに
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_key_sentences(text, max_sentences=3):
    """重要な文章を抽出"""
    if not text:
        return ""
    
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # 重要度指標となるキーワード
    important_keywords = [
        'AI', '人工知能', 'ChatGPT', 'OpenAI', 'Google', 'Apple', 'Microsoft', 'Amazon',
        '新機能', '新サービス', '発表', '公開', 'リリース', '開発', '投資',
        'スタートアップ', 'IPO', '買収', 'M&A', '資金調達',
        'iPhone', 'Android', 'iPad', 'Mac', 'Windows', 'Linux',
        '売上', '業績', '決算', '株価', '市場', '経済',
        '革新的', '画期的', '世界初', '最新', '注目', '話題'
    ]
    
    # 文章に重要度スコアを付与
    scored_sentences = []
    for sentence in sentences[:20]:  # 最初の20文を評価
        score = 0
        sentence_lower = sentence.lower()
        
        # キーワードマッチング
        for keyword in important_keywords:
            if keyword.lower() in sentence_lower:
                score += 2
        
        # 文章の長さによる調整（長すぎず短すぎない文章を優先）
        if 30 <= len(sentence) <= 150:
            score += 1
        
        # 数字や具体的なデータを含む文章
        if any(char.isdigit() for char in sentence):
            score += 1
            
        scored_sentences.append((sentence, score))
    
    # スコア順にソート
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    
    # 上位の文章を選択
    selected_sentences = [sent[0] for sent in scored_sentences[:max_sentences]]
    
    return '. '.join(selected_sentences) + '.'

def create_summary(text, max_length=SUMMARY_LENGTH):
    """高品質な要約を作成"""
    if not text:
        return ""
    
    # HTMLを除去
    clean_text = clean_html(text)
    
    # 重要な文章を抽出
    key_summary = extract_key_sentences(clean_text)
    
    # 長さ調整
    if len(key_summary) <= max_length:
        return key_summary
    
    # 長すぎる場合は調整
    truncated = key_summary[:max_length]
    last_period = truncated.rfind('.')
    if last_period > max_length * 0.7:
        truncated = truncated[:last_period + 1]
    else:
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:
            truncated = truncated[:last_space] + "..."
    
    return truncated

def extract_keywords(text):
    """高精度キーワード抽出"""
    if not text:
        return []
    
    # より豊富なキーワードデータベース
    keyword_categories = {
        "AI・機械学習": ["AI", "人工知能", "機械学習", "ChatGPT", "OpenAI", "Claude", "GPT", "LLM", "深層学習", "ニューラルネット"],
        "Apple製品": ["iPhone", "iPad", "MacBook", "Mac", "Apple Watch", "AirPods", "Apple TV", "iOS", "macOS"],
        "Google製品": ["Android", "Chrome", "Gmail", "Google Drive", "Pixel", "Chromebook", "YouTube"],
        "Microsoft": ["Windows", "Office", "Excel", "Surface", "Azure", "Teams", "OneDrive"],
        "Amazon": ["AWS", "Alexa", "Echo", "Prime", "Kindle", "Fire"],
        "ガジェット": ["スマートフォン", "スマホ", "タブレット", "ノートパソコン", "PC", "ワイヤレスイヤホン", "ヘッドホン", "スピーカー", "カメラ", "スマートウォッチ"],
        "プログラミング": ["Python", "JavaScript", "Java", "C++", "React", "Node.js", "GitHub", "Docker", "Kubernetes"],
        "ビジネス": ["スタートアップ", "IPO", "投資", "資金調達", "M&A", "買収", "売上", "業績", "決算", "株価"],
        "書籍・教育": ["本", "書籍", "電子書籍", "Kindle", "オンライン学習", "プログラミング学習", "資格", "セミナー"],
        "ゲーム": ["PlayStation", "Nintendo Switch", "Xbox", "Steam", "ゲーム", "eスポーツ"],
        "自動車・モビリティ": ["Tesla", "電気自動車", "EV", "自動運転", "カーシェア"],
        "暗号通貨": ["Bitcoin", "Ethereum", "NFT", "ブロックチェーン", "仮想通貨"]
    }
    
    found_keywords = []
    text_lower = text.lower()
    
    # カテゴリごとにキーワードを検索
    for category, keywords in keyword_categories.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
                
    # 重複除去と重要度順ソート
    unique_keywords = list(dict.fromkeys(found_keywords))
    
    # より関連性の高いキーワードを優先
    priority_keywords = ["AI", "iPhone", "ChatGPT", "Tesla", "Bitcoin", "Python", "React"]
    sorted_keywords = []
    
    # 優先キーワードを先に追加
    for keyword in priority_keywords:
        if keyword in unique_keywords:
            sorted_keywords.append(keyword)
            unique_keywords.remove(keyword)
    
    # 残りのキーワードを追加
    sorted_keywords.extend(unique_keywords)
    
    return sorted_keywords[:8]  # 最大8個に増加

def categorize_article(title, content, keywords):
    """高精度記事カテゴリ分類"""
    combined_text = f"{title} {content}".lower()
    
    # より詳細なカテゴリ分類
    categories = {
        "AI・機械学習": {
            "keywords": ["ai", "人工知能", "machine learning", "chatgpt", "openai", "claude", "gpt", "llm", "深層学習", "neural network", "tensorflow", "pytorch"],
            "score_threshold": 1
        },
        "Apple製品": {
            "keywords": ["iphone", "ipad", "macbook", "mac", "apple watch", "airpods", "ios", "macos", "apple", "tim cook"],
            "score_threshold": 1
        },
        "Google・Android": {
            "keywords": ["android", "google", "chrome", "pixel", "youtube", "gmail", "search", "alphabet"],
            "score_threshold": 1
        },
        "テクノロジー": {
            "keywords": ["technology", "tech", "software", "app", "cloud", "サーバー", "api", "database", "セキュリティ", "encryption"],
            "score_threshold": 2
        },
        "ガジェット": {
            "keywords": ["device", "smartphone", "tablet", "laptop", "camera", "headphone", "speaker", "watch", "ガジェット", "デバイス"],
            "score_threshold": 1
        },
        "プログラミング": {
            "keywords": ["programming", "code", "developer", "python", "javascript", "react", "node", "github", "プログラミング", "開発"],
            "score_threshold": 1
        },
        "ビジネス・投資": {
            "keywords": ["business", "startup", "investment", "ipo", "funding", "market", "economy", "stock", "ビジネス", "投資", "スタートアップ"],
            "score_threshold": 1
        },
        "ゲーム": {
            "keywords": ["game", "gaming", "playstation", "nintendo", "xbox", "steam", "esports", "ゲーム"],
            "score_threshold": 1
        },
        "自動車・EV": {
            "keywords": ["tesla", "electric vehicle", "ev", "自動運転", "autonomous", "car", "automotive", "電気自動車"],
            "score_threshold": 1
        },
        "暗号通貨・ブロックチェーン": {
            "keywords": ["bitcoin", "ethereum", "cryptocurrency", "blockchain", "nft", "defi", "crypto", "仮想通貨"],
            "score_threshold": 1
        }
    }
    
    category_scores = {}
    
    # キーワードベースのスコアリング
    for category, config in categories.items():
        score = 0
        for keyword in config["keywords"]:
            if keyword in combined_text:
                score += combined_text.count(keyword)
        
        # タイトル内のキーワードには重み付け
        title_lower = title.lower()
        for keyword in config["keywords"]:
            if keyword in title_lower:
                score += 2
        
        if score >= config["score_threshold"]:
            category_scores[category] = score
    
    # 最高スコアのカテゴリを選択
    if category_scores:
        best_category = max(category_scores, key=category_scores.get)
        return best_category
    
    # フォールバック分類
    if any(word in combined_text for word in ["book", "本", "書籍", "author", "読書"]):
        return "書籍・教育"
    elif any(word in combined_text for word in ["news", "politics", "world", "国際", "政治"]):
        return "ニュース・国際"
    
    return "テクノロジー"  # デフォルトカテゴリ

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
                # 日本語記事のみフィルタリング
                title = article.get("title", "")
                description = article.get("description", "")
                summary = article.get("summary", "")
                content = description if len(description) > len(summary) else summary
                
                # タイトルまたはコンテンツが日本語でない場合はスキップ
                if not is_japanese_text(title) and not is_japanese_text(content):
                    if DEBUG:
                        print(f"  - Skipped (non-Japanese): {title[:30]}...")
                    continue
                
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