# RSS Affiliate System

GitHub Pages + RSS自動取得 + アフィリエイトリンク生成システム

## 🎯 概要

毎日朝6時にGitHub Actionsが自動実行され、RSSフィードから記事を取得し、要約を作成してアフィリエイトリンク付きのWebページを生成します。

## 🏗️ システム構成

### パイプライン型アーキテクチャ
```
01_fetch_rss.py → 02_process_content.py → 03_add_affiliate.py → 04_generate_html.py
```

### ディレクトリ構造
```
rss_affiliate/
├── 01_fetch_rss.py           # RSS取得
├── 02_process_content.py     # 記事要約・処理
├── 03_add_affiliate.py       # アフィリエイトリンク追加
├── 04_generate_html.py       # HTML生成
├── run_all.py               # 全ステップ実行
├── config.py                # 設定ファイル
├── requirements.txt         # 依存関係
├── data/                    # 中間データ（デバッグ用）
│   ├── rss_raw.json
│   ├── articles_processed.json
│   └── articles_with_affiliate.json
├── output/                  # 最終HTML出力
│   └── index.html
├── templates/
│   └── index.html           # HTMLテンプレート
└── .github/workflows/
    └── daily_update.yml     # GitHub Actions設定
```

## 🚀 セットアップ

### 1. リポジトリ設定

```bash
# このディレクトリをGitリポジトリのルートに配置
git add rss_affiliate/
git commit -m "Add RSS affiliate system"
git push origin main
```

### 2. GitHub Pages有効化

1. GitHubリポジトリの Settings → Pages
2. Source: "GitHub Actions" を選択
3. 保存

### 3. 設定カスタマイズ

`config.py` を編集：

```python
# RSS Feed URLs（お好みのRSSフィードに変更）
RSS_FEEDS = [
    "https://rss.cnn.com/rss/edition.rss",
    "https://feeds.bbci.co.uk/news/rss.xml",
    # 追加したいRSSフィードをここに追加
]

# アフィリエイト設定
AFFILIATE_CONFIGS = {
    "amazon": {
        "tag": "your-amazon-tag-20",  # 🔧 Amazonアソシエイトタグに変更
        # ...
    },
    "rakuten": {
        "affiliate_id": "your-rakuten-id",  # 🔧 楽天IDに変更
        # ...
    }
}
```

## 🔧 ローカルテスト

### 個別ステップテスト
```bash
cd rss_affiliate

# 1. 依存関係インストール
pip install -r requirements.txt

# 2. 個別ステップテスト
python 01_fetch_rss.py
python 02_process_content.py
python 03_add_affiliate.py
python 04_generate_html.py

# 3. 全パイプライン実行
python run_all.py
```

### 生成ファイル確認
```bash
# 中間データ確認（デバッグ用）
cat data/rss_raw.json
cat data/articles_processed.json
cat data/articles_with_affiliate.json

# 最終HTML確認
open output/index.html  # macOS
# または
start output/index.html  # Windows
```

## ⏰ 自動実行スケジュール

- **毎日朝6時（JST）** - GitHub Actionsで自動実行
- **手動実行** - GitHub リポジトリの Actions タブから実行可能
- **プッシュ時** - `rss_affiliate/` 配下のファイル変更時に自動実行

## 📊 特徴

### デバッグフレンドリー
- 各ステップで中間データをJSONで保存
- 問題箇所の特定が容易
- 個別ステップでのテスト実行可能

### スマートなアフィリエイト
- キーワードベースの自動マッチング
- カテゴリ別の商品推薦
- Amazon・楽天の複数プラットフォーム対応

### 美しいUI
- レスポンシブデザイン
- カテゴリ別色分け
- アフィリエイトリンクの視覚的区別

## 🔧 カスタマイズ

### RSSフィード追加
`config.py` の `RSS_FEEDS` リストに追加：
```python
RSS_FEEDS = [
    "https://example.com/rss.xml",
    # 新しいフィードをここに追加
]
```

### アフィリエイト戦略変更
`03_add_affiliate.py` の `category_strategies` を編集：
```python
category_strategies = {
    "tech": ["amazon", "rakuten"],
    "book": ["amazon"],
    # カスタマイズ
}
```

### HTMLテンプレート
`templates/index.html` を自由に編集可能

## 📈 収益化例

- **テック記事** → プログラミング本、開発ツール
- **ガジェット記事** → スマホアクセサリー、最新デバイス  
- **書籍記事** → 関連書籍、Kindle Unlimited
- **ビジネス記事** → ビジネス書、スキルアップ教材

## 🚨 トラブルシューティング

### GitHub Actions失敗時
1. Actions タブで詳細ログを確認
2. RSS フィードの可用性をチェック
3. アフィリエイトタグの設定確認

### ローカルテスト失敗時
```bash
# デバッグモードで実行
python -c "
import config
config.DEBUG = True
config.VERBOSE = True
"
python run_all.py
```

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**🎉 準備完了！** コミット・プッシュ後、GitHub Actionsが自動実行されます。# Manual trigger for GitHub Actions
