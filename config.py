# RSS Affiliate System Configuration

import os
from datetime import datetime

# RSS Feed URLs
RSS_FEEDS = [
    # テクノロジー・IT
    "https://techcrunch.com/feed/",
    "https://feeds.feedburner.com/oreilly/radar",
    "https://www.theverge.com/rss/index.xml",
    "https://arstechnica.com/feed/",
    "https://feeds.feedburner.com/venturebeat/SZYF",
    "https://feeds.feedburner.com/Techcrunch",
    "https://feeds.feedburner.com/TechCrunchJapan",
    "https://feeds.feedburner.com/wired/index",
    "https://feeds.feedburner.com/engadget/all",
    "https://feeds.feedburner.com/gizmodo/iqyf",
    
    # ビジネス・経済
    "https://feeds.feedburner.com/entrepreneur/latest",
    "https://feeds.feedburner.com/fastcompany/all",
    "https://feeds.feedburner.com/inc/articles",
    "https://feeds.feedburner.com/time/topstories",
    "https://www.reuters.com/technology/feed/",
    "https://feeds.feedburner.com/reuters/technologyNews",
    
    # 日本語メディア
    "https://japan.cnet.com/rss/index.rdf",
    "https://feeds.feedburner.com/itmedia/all",
    "https://feeds.feedburner.com/impressWatch",
    "https://www.publickey1.jp/atom.xml",
    "https://gihyo.jp/feed/rss",
    "https://diamond.jp/list/feed/",
    
    # 国際ニュース
    "https://rss.cnn.com/rss/edition.rss",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.washingtonpost.com/rss/technology",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://feeds.feedburner.com/thenextweb",
    
    # プロダクト・ガジェット
    "https://feeds.feedburner.com/TheAppleBlog",
    "https://feeds.feedburner.com/AndroidCentral-News",
    "https://9to5mac.com/feed/",
    "https://9to5google.com/feed/",
    "https://www.androidpolice.com/feed/",
    
    # AI・機械学習
    "https://feeds.feedburner.com/oreilly/ai",
    "https://towardsdatascience.com/feed",
    "https://feeds.feedburner.com/kdnuggets-data-mining-analytics",
    "https://machinelearningmastery.com/feed/",
    
    # スタートアップ
    "https://feeds.feedburner.com/crunchbase",
    "https://feeds.feedburner.com/PandoDaily",
    "https://feeds.feedburner.com/startup"
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