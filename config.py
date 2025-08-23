# RSS Affiliate System Configuration

import os
from datetime import datetime, timezone, timedelta

# RSS Feed URLs - 日本語メディア
RSS_FEEDS = [
    # 主要テック・ITメディア
    "https://japan.cnet.com/rss/index.rdf",
    "https://www.publickey1.jp/atom.xml",
    "https://feeds.feedburner.com/itmedia/all",
    "https://feeds.feedburner.com/impressWatch", 
    "https://gihyo.jp/feed/rss",
    "https://feeds.feedburner.com/TechCrunchJapan",
    "https://news.mynavi.jp/rss/techplus",
    "https://ascii.jp/rss.xml",
    "https://www.4gamer.net/games/999/G999902/rss.xml",
    
    # Watch系メディア
    "https://pc.watch.impress.co.jp/data/rss.rdf",
    "https://k-tai.watch.impress.co.jp/data/rss.rdf",
    "https://car.watch.impress.co.jp/data/rss.rdf",
    "https://av.watch.impress.co.jp/data/rss.rdf",
    "https://game.watch.impress.co.jp/data/rss.rdf",
    "https://internet.watch.impress.co.jp/data/rss.rdf",
    
    # ビジネス・経済メディア
    "https://diamond.jp/list/feed/",
    "https://toyokeizai.net/list/feed.rss",
    "https://newspicks.com/topics/rss",
    
    # エンジニア向けメディア
    "https://zenn.dev/feed",
    "https://qiita.com/popular-items/feed.atom",
    
    # Apple・ガジェット系
    "https://iphone-mania.jp/feed/",
    "https://taisy0.com/feed",
    
    # 総合ニュースサイト
    "https://www.sankei.com/xml/rss/economy.xml",
    "https://news.yahoo.co.jp/rss/topics/it.xml"
]

# Content Processing
MAX_ARTICLES_PER_FEED = 20  # 記事数を大幅に増加（数日分）
SUMMARY_LENGTH = 800  # より長い詳細な要約
ARTICLES_PER_PAGE = 12  # ページネーション用

# Affiliate Settings
AFFILIATE_CONFIGS = {
    "amazon": {
        "tag": "toy1021-22",
        "keywords": ["book", "kindle", "device", "gadget"],
        "search_base_url": "https://www.amazon.co.jp/s?k="
    },
    "rakuten": {
        "affiliate_id": "your-rakuten-id",
        "keywords": ["電子書籍", "ガジェット", "スマホ", "PC"],
        "search_base_url": "https://search.rakuten.co.jp/search/mall/"
    }
}

# Output Settings
DATA_DIR = "data"
OUTPUT_DIR = "output"
HTML_TEMPLATE_PATH = "templates/index.html"

# File Paths
RSS_RAW_FILE = os.path.join(DATA_DIR, "rss_raw.json")
PROCESSED_ARTICLES_FILE = os.path.join(DATA_DIR, "articles_processed.json")
AFFILIATE_ARTICLES_FILE = os.path.join(DATA_DIR, "articles_with_affiliate.json")
FINAL_HTML_FILE = os.path.join(OUTPUT_DIR, "index.html")

# Site Info
SITE_TITLE = "Tech News & Affiliate Hub"
SITE_DESCRIPTION = "Latest tech news with curated product recommendations"
# 日本時間（JST）でUPDATE_TIMEを生成
JST = timezone(timedelta(hours=9))
UPDATE_TIME = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")

# Debug Settings
DEBUG = True
VERBOSE = True