#!/usr/bin/env python3

import feedparser
import json
import os
import requests
from datetime import datetime
from config import RSS_FEEDS, RSS_RAW_FILE, DATA_DIR, MAX_ARTICLES_PER_FEED, DEBUG, VERBOSE

def fetch_rss_feed(url):
    """単一のRSSフィードを取得"""
    try:
        if VERBOSE:
            print(f"Fetching RSS from: {url}")
        
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
        
        return {
            "feed_url": url,
            "feed_title": feed.feed.get("title", "Unknown"),
            "feed_description": feed.feed.get("description", ""),
            "articles": articles,
            "total_articles": len(articles)
        }
        
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
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