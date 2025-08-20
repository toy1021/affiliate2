#!/usr/bin/env python3

import json
import os
from datetime import datetime, timezone
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

def get_relative_time(timestamp):
    """相対時間を日本語で返す"""
    now = datetime.now(timezone.utc)
    diff = now - timestamp
    
    if diff.days > 7:
        return timestamp.strftime("%m/%d")
    elif diff.days > 0:
        return f"{diff.days}日前"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}時間前"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}分前"
    else:
        return "たった今"

def parse_article_timestamp(article):
    """記事のタイムスタンプをパースしてdatetimeオブジェクトを返す"""
    published = article.get("published", "")
    fetched = article.get("fetched_at", "")
    
    # 公開日時を優先、なければ取得日時を使用
    timestamp_str = published if published else fetched
    
    if not timestamp_str:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    
    try:
        # 既存の日付フォーマットをパース
        if "T" in timestamp_str:
            # ISOフォーマットの場合
            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except:
                # シンプルISOフォーマット
                dt = datetime.strptime(timestamp_str[:19], "%Y-%m-%dT%H:%M:%S")
                return dt.replace(tzinfo=timezone.utc)
        else:
            # 簡単な日付フォーマットの場合
            dt = datetime.strptime(timestamp_str[:19], "%Y-%m-%d %H:%M:%S")
            return dt.replace(tzinfo=timezone.utc)
    except:
        try:
            # RFC2822フォーマットの場合（RSSでよく使われる）
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(timestamp_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except:
            return datetime(1970, 1, 1, tzinfo=timezone.utc)

def sort_articles(articles):
    """記事を時系列順（新しい順）でソート"""
    def sort_key(article):
        # タイムスタンプをパース
        timestamp = parse_article_timestamp(article)
        
        # 重要度スコア（同じ時刻の記事の場合のソート用）
        importance = calculate_article_importance(article)
        
        # 時系列を主要基準、重要度を副次基準とする
        return (timestamp, importance)
    
    sorted_articles = sorted(articles, key=sort_key, reverse=True)
    
    if VERBOSE:
        print(f"Sorted {len(sorted_articles)} articles by timestamp (newest first)")
        # トップ5記事のタイムスタンプを表示
        for i, article in enumerate(sorted_articles[:5]):
            timestamp = parse_article_timestamp(article)
            print(f"  #{i+1}: {article.get('title', 'Unknown')[:50]}... (Time: {timestamp})")
    
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
        
        # タイムスタンプのパースとフォーマット
        timestamp = parse_article_timestamp(article)
        
        # API用のISOフォーマット
        enhanced_article["timestamp"] = timestamp.isoformat()
        enhanced_article["timestamp_unix"] = int(timestamp.timestamp())
        
        # 表示用フォーマット
        try:
            enhanced_article["published_formatted"] = timestamp.strftime("%Y-%m-%d %H:%M")
            enhanced_article["published_date_only"] = timestamp.strftime("%Y-%m-%d")
            enhanced_article["published_time_only"] = timestamp.strftime("%H:%M")
            enhanced_article["published_relative"] = get_relative_time(timestamp)
        except:
            enhanced_article["published_formatted"] = "不明"
            enhanced_article["published_date_only"] = "不明"
            enhanced_article["published_time_only"] = ""
            enhanced_article["published_relative"] = "不明"
        
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

def generate_sitemap_xml(articles):
    """SEO用のサイトマップXMLを生成"""
    from xml.etree.ElementTree import Element, SubElement, tostring
    from xml.dom import minidom
    
    # URLセット要素を作成
    urlset = Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:news', 'http://www.google.com/schemas/sitemap-news/0.9')
    
    # メインページ
    url = SubElement(urlset, 'url')
    SubElement(url, 'loc').text = 'https://toy1021.github.io/affiliate2/'
    SubElement(url, 'lastmod').text = UPDATE_TIME.replace(' ', 'T') + '+09:00'
    SubElement(url, 'changefreq').text = 'hourly'
    SubElement(url, 'priority').text = '1.0'
    
    # 各記事（最新50件のみ、検索エンジンの負荷軽減）
    for article in articles[:50]:
        if not article.get('link'):
            continue
            
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = article['link']
        
        # 記事の最終更新日
        if article.get('published'):
            try:
                # ISO形式に変換
                timestamp = parse_article_timestamp(article)
                SubElement(url, 'lastmod').text = timestamp.strftime('%Y-%m-%dT%H:%M:%S+09:00')
            except:
                SubElement(url, 'lastmod').text = UPDATE_TIME.replace(' ', 'T') + '+09:00'
        
        SubElement(url, 'changefreq').text = 'daily'
        SubElement(url, 'priority').text = '0.8'
        
        # Googleニュース用の追加情報（最新24時間以内の記事のみ）
        try:
            article_time = parse_article_timestamp(article)
            time_diff = datetime.now(timezone.utc) - article_time
            if time_diff.days == 0:  # 24時間以内
                news = SubElement(url, 'news:news')
                publication = SubElement(news, 'news:publication')
                SubElement(publication, 'news:name').text = 'テックニュース速報'
                SubElement(publication, 'news:language').text = 'ja'
                SubElement(news, 'news:publication_date').text = article_time.strftime('%Y-%m-%d')
                SubElement(news, 'news:title').text = article.get('title', '')
        except:
            pass  # ニュース用タグの追加に失敗しても続行
    
    # XMLを整形
    rough_string = tostring(urlset, 'unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ").replace('<?xml version="1.0" ?>\n', 
                                                     '<?xml version="1.0" encoding="UTF-8"?>\n')

def generate_sitemap(articles, total_pages=1):
    """簡単なサイトマップ情報を生成（将来の拡張用）"""
    sitemap_data = {
        "generated_at": datetime.now().isoformat(),
        "total_pages": total_pages,
        "articles_count": len(articles),
        "last_updated": UPDATE_TIME
    }
    
    return sitemap_data

def generate_category_menu(all_articles):
    """全記事からカテゴリメニューを生成"""
    category_stats = {}
    
    # カテゴリ別記事数をカウント
    for article in all_articles:
        category = article.get("category", "一般")
        if category not in category_stats:
            category_stats[category] = 0
        category_stats[category] += 1
    
    # カテゴリを記事数の多い順でソート
    sorted_categories = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_categories

def generate_sources_menu(all_articles):
    """全記事から情報源メニューを生成"""
    sources_info = {}
    
    # ソース別記事数をカウントし、URLも保存
    for article in all_articles:
        source_name = article.get("source_name", "Unknown")
        source_feed = article.get("source_feed", "")
        
        if source_name not in sources_info:
            # フィードURLからメインサイトURLを推定
            main_url = ""
            if source_feed:
                if "cnet.com" in source_feed:
                    main_url = "https://japan.cnet.com/"
                elif "publickey1.jp" in source_feed:
                    main_url = "https://www.publickey1.jp/"
                elif "itmedia" in source_feed:
                    main_url = "https://www.itmedia.co.jp/"
                elif "impress" in source_feed:
                    main_url = "https://www.watch.impress.co.jp/"
                elif "gihyo.jp" in source_feed:
                    main_url = "https://gihyo.jp/"
                elif "techcrunch" in source_feed:
                    main_url = "https://jp.techcrunch.com/"
                elif "mynavi" in source_feed:
                    main_url = "https://news.mynavi.jp/"
                elif "ascii.jp" in source_feed:
                    main_url = "https://ascii.jp/"
                elif "4gamer" in source_feed:
                    main_url = "https://www.4gamer.net/"
                elif "diamond.jp" in source_feed:
                    main_url = "https://diamond.jp/"
                elif "toyokeizai" in source_feed:
                    main_url = "https://toyokeizai.net/"
                elif "newspicks" in source_feed:
                    main_url = "https://newspicks.com/"
                elif "zenn.dev" in source_feed:
                    main_url = "https://zenn.dev/"
                elif "qiita.com" in source_feed:
                    main_url = "https://qiita.com/"
                elif "iphone-mania" in source_feed:
                    main_url = "https://iphone-mania.jp/"
                elif "taisy0.com" in source_feed:
                    main_url = "https://taisy0.com/"
                elif "sankei" in source_feed:
                    main_url = "https://www.sankei.com/"
                elif "yahoo.co.jp" in source_feed:
                    main_url = "https://news.yahoo.co.jp/"
                else:
                    # ドメインを抽出してメインURLを作成
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(source_feed)
                        main_url = f"{parsed.scheme}://{parsed.netloc}/"
                    except:
                        main_url = source_feed
            
            sources_info[source_name] = {
                "count": 0,
                "url": main_url,
                "feed_url": source_feed
            }
        
        sources_info[source_name]["count"] += 1
    
    # 記事数の多い順でソート
    sorted_sources = sorted(sources_info.items(), key=lambda x: x[1]["count"], reverse=True)
    
    return sorted_sources

def generate_api_data(enhanced_articles, stats):
    """記事データをJSON API用に出力"""
    category_menu = generate_category_menu(enhanced_articles)
    sources_menu = generate_sources_menu(enhanced_articles)
    
    api_data = {
        "meta": {
            "total_articles": stats["total_articles"],
            "total_pages": (len(enhanced_articles) + ARTICLES_PER_PAGE - 1) // ARTICLES_PER_PAGE,
            "articles_per_page": ARTICLES_PER_PAGE,
            "total_affiliate_links": stats["total_affiliate_links"],
            "total_feeds": stats["total_feeds"],
            "last_updated": UPDATE_TIME,
            "generated_at": datetime.now().isoformat()
        },
        "categories": [{
            "name": category,
            "count": count
        } for category, count in category_menu],
        "sources": [{
            "name": source_name,
            "url": source_info["url"],
            "count": source_info["count"]
        } for source_name, source_info in sources_menu],
        "articles": enhanced_articles
    }
    
    # JSONファイルとして出力
    api_file = os.path.join(OUTPUT_DIR, "articles.json")
    with open(api_file, 'w', encoding='utf-8') as f:
        json.dump(api_data, f, ensure_ascii=False, indent=2)
    
    if VERBOSE:
        print(f"API data saved: {api_file}")
    
    return api_data

def generate_spa_as_main(enhanced_articles, stats):
    """SPAをメインのindex.htmlとして生成"""
    # SPA用テンプレートを読み込み
    spa_template_path = "templates/spa.html"
    
    if not os.path.exists(spa_template_path):
        print(f"Error: SPA template not found: {spa_template_path}")
        return None
    
    with open(spa_template_path, 'r', encoding='utf-8') as f:
        spa_content = f.read()
    
    # メインのindex.htmlとして出力
    main_output_file = FINAL_HTML_FILE
    with open(main_output_file, 'w', encoding='utf-8') as f:
        f.write(spa_content)
    
    if VERBOSE:
        print(f"SPA generated as main page: {main_output_file}")
    
    return [main_output_file]

def generate_spa_version(enhanced_articles, stats):
    """シングルページアプリケーション版を生成"""
    # SPA用テンプレートを読み込み
    spa_template_path = "templates/spa.html"
    
    if not os.path.exists(spa_template_path):
        print(f"Warning: SPA template not found: {spa_template_path}")
        return None
    
    with open(spa_template_path, 'r', encoding='utf-8') as f:
        spa_content = f.read()
    
    # SPA用HTMLファイルを出力
    spa_output_file = os.path.join(OUTPUT_DIR, "spa.html")
    with open(spa_output_file, 'w', encoding='utf-8') as f:
        f.write(spa_content)
    
    if VERBOSE:
        print(f"SPA version generated: {spa_output_file}")
    
    return spa_output_file

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
    
    # APIデータ生成
    api_data = generate_api_data(enhanced_articles, stats)
    
    # SPA版生成
    spa_file = generate_spa_version(enhanced_articles, stats)
    
    # SPA版をメインページとして生成
    try:
        generated_files = generate_spa_as_main(enhanced_articles, stats)
        
        print(f"\n=== Summary ===")
        print(f"SPA page generated: {len(generated_files)}")
        print(f"Total articles: {stats['total_articles']}")
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
        
        # サイトマップXML生成（SEO用）
        sitemap_xml = generate_sitemap_xml(enhanced_articles)
        sitemap_xml_file = os.path.join(OUTPUT_DIR, "sitemap.xml")
        with open(sitemap_xml_file, 'w', encoding='utf-8') as f:
            f.write(sitemap_xml)
        
        if VERBOSE:
            print(f"Sitemap XML saved: {sitemap_xml_file}")
        
        # サイトマップJSON情報生成（統計用）
        sitemap = generate_sitemap(enhanced_articles, 1)  # SPAは1ページ
        sitemap_file = os.path.join(OUTPUT_DIR, "sitemap.json")
        with open(sitemap_file, 'w', encoding='utf-8') as f:
            json.dump(sitemap, f, ensure_ascii=False, indent=2)
        
        if VERBOSE:
            print(f"Sitemap data saved: {sitemap_file}")
        
        # ファイルサイズ確認
        main_file_size = os.path.getsize(FINAL_HTML_FILE)
        print(f"SPA page size: {main_file_size:,} bytes")
        
        print(f"\n✅ Ready for GitHub Pages deployment!")
        
    except Exception as e:
        print(f"Error generating HTML: {e}")
        raise

if __name__ == "__main__":
    main()