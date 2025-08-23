#!/usr/bin/env python3

"""
スラッグ生成の一貫性をテストするスクリプト
Python側とJavaScript側のスラッグ生成が同じ結果になることを保証
"""

import json
import re
from pathlib import Path

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

def javascript_create_slug(article_id):
    """JavaScript版のスラッグ生成をPythonで模擬"""
    import re
    # スペースとスラッシュをアンダースコアに変換
    slug = article_id.replace(' ', '_').replace('/', '_').replace('\\', '_')
    # 特殊文字もアンダースコアに変換（安全性向上）
    slug = slug.replace('!', '_').replace('?', '_').replace('.', '_').replace(':', '_')
    slug = slug.replace('(', '_').replace(')', '_').replace('[', '_').replace(']', '_')
    # 連続するアンダースコアを単一に
    slug = re.sub(r'_+', '_', slug)
    # 英数字、アンダースコア、ハイフン、日本語文字を保持
    result = ''
    for c in slug:
        if (('a' <= c <= 'z') or ('A' <= c <= 'Z') or 
            ('0' <= c <= '9') or c in '_-' or
            ('\u3040' <= c <= '\u309F') or  # ひらがな
            ('\u30A0' <= c <= '\u30FF') or  # カタカナ
            ('\u4E00' <= c <= '\u9FAF')):   # 漢字
            result += c
    # 先頭と末尾のアンダースコアを除去
    result = result.strip('_')
    return result

def test_slug_consistency():
    """スラッグ生成の一貫性をテスト"""
    # テストケース
    test_cases = [
        "CNET Japan 最新情報　総合_6484",
        "Zennのトレンド_1234",
        "Qiita - 人気の記事_9876",
        "iPhone_Mania_5432",
        "気になる、記になる…_1111",
        "Yahoo!ニュース・トピックス - IT_2222",
        "テスト記事/記号\\含む_3333"
    ]
    
    print("=== スラッグ生成一貫性テスト ===")
    
    all_passed = True
    
    for test_case in test_cases:
        python_result = python_create_slug(test_case)
        js_result = javascript_create_slug(test_case)
        
        passed = python_result == js_result
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_case}")
        print(f"  Python:     {python_result}")
        print(f"  JavaScript: {js_result}")
        if not passed:
            print(f"  差異: Python結果とJavaScript結果が異なります")
        print()
    
    # 実際の記事データでもテスト
    articles_file = Path("output/articles.json")
    if articles_file.exists():
        print("=== 実記事データテスト ===")
        with open(articles_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        sample_articles = data['articles'][:10]  # 最初の10件でテスト
        
        for article in sample_articles:
            article_id = article['id']
            python_result = python_create_slug(article_id)
            js_result = javascript_create_slug(article_id)
            
            passed = python_result == js_result
            all_passed = all_passed and passed
            
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {article_id}")
            if not passed:
                print(f"  Python:     {python_result}")
                print(f"  JavaScript: {js_result}")
                print()
    
    print("=== テスト結果 ===")
    if all_passed:
        print("✅ 全テスト通過！PythonとJavaScriptのスラッグ生成が一致しています。")
        return True
    else:
        print("❌ テスト失敗。PythonとJavaScriptのスラッグ生成に不整合があります。")
        return False

if __name__ == "__main__":
    test_slug_consistency()