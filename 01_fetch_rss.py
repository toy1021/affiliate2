#!/usr/bin/env python3

import feedparser
import json
import os
import requests
import hashlib
from datetime import datetime, timedelta
from config import RSS_FEEDS, RSS_RAW_FILE, DATA_DIR, MAX_ARTICLES_PER_FEED, DEBUG, VERBOSE

def get_cache_key(url):
    """URLからキャッシュキーを生成"""
    return hashlib.md5(url.encode()).hexdigest()

def is_cache_valid(cache_file, max_age_minutes=45):
    """キャッシュが有効かチェック（1時間間隔用に45分で設定）"""
    if not os.path.exists(cache_file):
        return False
    
    cache_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
    return datetime.now() - cache_time < timedelta(minutes=max_age_minutes)

def fetch_rss_feed(url):
    """単一のRSSフィードを取得（キャッシュ機能付き）"""
    try:
        # キャッシュファイルパス
        cache_key = get_cache_key(url)
        cache_file = os.path.join(DATA_DIR, f"cache_{cache_key}.json")
        
        # キャッシュが有効な場合は使用
        if is_cache_valid(cache_file):
            if VERBOSE:
                print(f"Using cached data for: {url}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        if VERBOSE:
            print(f"Fetching fresh RSS from: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        
        if feed.bozo:
            print(f"Warning: Feed parsing error for {url}: {feed.bozo_exception}")
        
        articles = []
        for entry in feed.entries[:MAX_ARTICLES_PER_FEED]:
            article = {
                "title": entry.get("title", "No title"),
                "link": entry.get("link", ""),
                "description": entry.get("description", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", ""),
                "published_parsed": entry.get("published_parsed", None),
                "source_feed": url,
                "source_name": feed.feed.get("title", url),
                "tags": [tag.term for tag in entry.get("tags", [])],
                "fetched_at": datetime.now().isoformat()
            }
            articles.append(article)
        
        if VERBOSE:
            print(f"Fetched {len(articles)} articles from {feed.feed.get('title', url)}")
        
        result = {
            "feed_url": url,
            "feed_title": feed.feed.get("title", "Unknown"),
            "feed_description": feed.feed.get("description", ""),
            "articles": articles,
            "total_articles": len(articles),
            "cached_at": datetime.now().isoformat()
        }
        
        # キャッシュに保存
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as cache_error:
            if VERBOSE:
                print(f"Cache write error for {url}: {cache_error}")
        
        return result
        
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        # 既存キャッシュがあれば古いデータでも返す（フォールバック）
        try:
            cache_key = get_cache_key(url)
            fallback_cache = os.path.join(DATA_DIR, f"cache_{cache_key}.json")
            if os.path.exists(fallback_cache):
                if VERBOSE:
                    print(f"Using stale cache as fallback for: {url}")
                with open(fallback_cache, 'r', encoding='utf-8') as f:
                    fallback_data = json.load(f)
                    fallback_data["is_fallback"] = True
                    return fallback_data
        except Exception as fallback_error:
            if VERBOSE:
                print(f"Fallback cache read error: {fallback_error}")
        return None
    except Exception as e:
        print(f"Unexpected error processing {url}: {e}")
        return None

def main():
    """メイン処理"""
    print("=== RSS Feed Fetcher ===")
    
    # データディレクトリ作成
    os.makedirs(DATA_DIR, exist_ok=True)
    
    all_feeds_data = []
    total_articles = 0
    
    for feed_url in RSS_FEEDS:
        feed_data = fetch_rss_feed(feed_url)
        if feed_data:
            all_feeds_data.append(feed_data)
            total_articles += feed_data["total_articles"]
        else:
            print(f"Failed to fetch feed: {feed_url}")
    
    # 結果をJSONファイルに保存
    output_data = {
        "fetch_timestamp": datetime.now().isoformat(),
        "total_feeds": len(all_feeds_data),
        "total_articles": total_articles,
        "feeds": all_feeds_data
    }
    
    with open(RSS_RAW_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Summary ===")
    print(f"Total feeds processed: {len(all_feeds_data)}")
    print(f"Total articles fetched: {total_articles}")
    print(f"Data saved to: {RSS_RAW_FILE}")
    
    if DEBUG:
        print(f"\nSample article:")
        if all_feeds_data and all_feeds_data[0]["articles"]:
            sample = all_feeds_data[0]["articles"][0]
            print(f"Title: {sample['title']}")
            print(f"Source: {sample['source_name']}")
            print(f"Link: {sample['link']}")

if __name__ == "__main__":
    main()