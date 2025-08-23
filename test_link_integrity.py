#!/usr/bin/env python3

"""
リンク整合性テスト
- 生成されたHTMLファイルと実際のリンクの整合性を確認
- 404になる可能性のあるリンクを事前検出
"""

import json
import os
from pathlib import Path
import re

def python_create_slug(article_id):
    """Python版のスラッグ生成（04_generate_html.pyと同じ）"""
    import re
    # スペースとスラッシュをアンダースコアに変換
    slug = article_id.replace(' ', '_').replace('/', '_').replace('\\', '_')
    # 特殊文字もアンダースコアに変換（安全性向上）
    slug = slug.replace('!', '_').replace('?', '_').replace('.', '_').replace(':', '_')
    slug = slug.replace('(', '_').replace(')', '_').replace('[', '_').replace(']', '_')
    # 連続するアンダースコアを単一に
    slug = re.sub(r'_+', '_', slug)
    # 英数字、アンダースコア、ハイフン、日本語文字を保持
    def is_valid_char(c):
        return (c.isascii() and c.isalnum()) or c in '_-' or (
            '\u3040' <= c <= '\u309F' or  # ひらがな
            '\u30A0' <= c <= '\u30FF' or  # カタカナ
            '\u4E00' <= c <= '\u9FAF'     # 漢字
        )
    slug = ''.join(c for c in slug if is_valid_char(c))
    # 先頭と末尾のアンダースコアを除去
    slug = slug.strip('_')
    return slug

def test_link_integrity():
    """リンク整合性をテスト"""
    print("=== リンク整合性テスト ===")
    
    # articles.jsonを読み込み
    articles_file = Path("output/articles.json")
    if not articles_file.exists():
        print("❌ output/articles.json が見つかりません")
        return False
        
    with open(articles_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    missing_files = []
    total_articles = len(data['articles'])
    
    print(f"📄 {total_articles}件の記事をチェック中...")
    
    for article in data['articles']:
        article_id = article['id']
        expected_slug = python_create_slug(article_id)
        expected_file = Path(f"output/articles/{expected_slug}.html")
        
        if not expected_file.exists():
            missing_files.append({
                'article_id': article_id,
                'expected_slug': expected_slug,
                'expected_file': str(expected_file),
                'title': article.get('title', '')[:50] + "..."
            })
    
    if missing_files:
        print(f"❌ {len(missing_files)}件のファイルが見つかりません:")
        for missing in missing_files:
            print(f"  ID: {missing['article_id']}")
            print(f"  タイトル: {missing['title']}")
            print(f"  期待ファイル: {missing['expected_file']}")
            print()
        return False
    else:
        print(f"✅ 全{total_articles}件のHTMLファイルが存在します")
    
    # index.htmlのリンクチェック
    print("\n=== index.htmlのリンクチェック ===")
    index_file = Path("output/index.html")
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # createSlug関数を抽出
        slug_function_match = re.search(r'createSlug\(articleId\)[^}]+}', html_content, re.DOTALL)
        if slug_function_match:
            print("✅ createSlug関数が見つかりました")
            
            # 日本語文字対応の確認
            if '\\u3040' in html_content and '\\u30A0' in html_content and '\\u4E00' in html_content:
                print("✅ JavaScript側で日本語文字対応済み")
            else:
                print("❌ JavaScript側で日本語文字対応が不完全")
                return False
        else:
            print("❌ createSlug関数が見つかりません")
            return False
    
    print("\n=== テスト結果 ===")
    print("✅ 全てのテストに合格しました！")
    return True

if __name__ == "__main__":
    success = test_link_integrity()
    exit(0 if success else 1)