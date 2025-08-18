# RSS Affiliate System Configuration

import os
from datetime import datetime

# RSS Feed URLs
RSS_FEEDS = [
    "https://rss.cnn.com/rss/edition.rss",  # CNN
    "https://feeds.bbci.co.uk/news/rss.xml",  # BBC
    "https://techcrunch.com/feed/",  # TechCrunch
    "https://feeds.feedburner.com/oreilly/radar",  # O'Reilly Radar
]

# Content Processing
MAX_ARTICLES_PER_FEED = 5
SUMMARY_LENGTH = 200  # characters

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