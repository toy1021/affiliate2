# RSS Affiliate System Configuration

import os
from datetime import datetime

# RSS Feed URLs - 日本語メディアのみ
RSS_FEEDS = [
    # 日本語テック・ITメディア
    "https://japan.cnet.com/rss/index.rdf",
    "https://www.publickey1.jp/atom.xml",
    "https://feeds.feedburner.com/itmedia/all",
    "https://feeds.feedburner.com/impressWatch", 
    "https://gihyo.jp/feed/rss",
    "https://diamond.jp/list/feed/",
    "https://feeds.feedburner.com/TechCrunchJapan",
    
    # 追加の日本語メディア
    "https://news.mynavi.jp/rss/techplus",
    "https://ascii.jp/rss.xml",
    "https://www.4gamer.net/games/999/G999902/rss.xml",
    "https://car.watch.impress.co.jp/data/rss.rdf",
    "https://pc.watch.impress.co.jp/data/rss.rdf",
    "https://k-tai.watch.impress.co.jp/data/rss.rdf"
]

# Content Processing
MAX_ARTICLES_PER_FEED = 8  # 記事数を増加
SUMMARY_LENGTH = 350  # より詳細な要約

# Affiliate Settings
AFFILIATE_CONFIGS = {
    "amazon": {
        "tag": "your-amazon-tag-20",
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
UPDATE_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Debug Settings
DEBUG = True
VERBOSE = True