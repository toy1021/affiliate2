#!/usr/bin/env python3

import subprocess
import sys
import time
import os
from datetime import datetime
from config import DEBUG, VERBOSE

def run_script(script_name, description):
    """Pythonスクリプトを実行"""
    print(f"\n{'='*50}")
    print(f"🚀 {description}")
    print(f"{'='*50}")
    
    start_time = time.time()
    
    try:
        # スクリプトの存在確認
        if not os.path.exists(script_name):
            print(f"❌ Error: {script_name} not found")
            return False
        
        # スクリプト実行
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=300  # 5分でタイムアウト
        )
        
        duration = time.time() - start_time
        
        # 標準出力を表示
        if result.stdout:
            print(result.stdout)
        
        # エラー出力があれば表示
        if result.stderr:
            print(f"⚠️ Warnings/Errors:")
            print(result.stderr)
        
        # 実行結果判定
        if result.returncode == 0:
            print(f"✅ {description} completed successfully ({duration:.1f}s)")
            return True
        else:
            print(f"❌ {description} failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Unexpected error in {description}: {e}")
        return False

def check_requirements():
    """必要な依存関係をチェック"""
    print("🔍 Checking requirements...")
    
    required_files = [
        "01_fetch_rss.py",
        "02_process_content.py", 
        "03_add_affiliate.py",
        "04_generate_html.py",
        "config.py",
        "requirements.txt",
        "templates/spa.html"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def create_directories():
    """必要なディレクトリを作成"""
    directories = ["data", "output"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        if VERBOSE:
            print(f"📁 Directory ready: {directory}/")

def cleanup_old_data(keep_backups=True):
    """古いデータをクリーンアップ（オプション）"""
    if not keep_backups:
        return
    
    data_files = [
        "data/rss_raw.json",
        "data/articles_processed.json", 
        "data/articles_with_affiliate.json"
    ]
    
    # バックアップ作成
    backup_suffix = datetime.now().strftime("_%Y%m%d_%H%M%S")
    
    for file in data_files:
        if os.path.exists(file):
            backup_file = f"{file}.backup{backup_suffix}"
            try:
                os.rename(file, backup_file)
                if VERBOSE:
                    print(f"📦 Backup created: {backup_file}")
            except Exception as e:
                print(f"⚠️ Could not backup {file}: {e}")

def generate_report(results):
    """実行結果レポートを生成"""
    print(f"\n{'='*60}")
    print(f"📊 EXECUTION REPORT")
    print(f"{'='*60}")
    
    total_steps = len(results)
    successful_steps = sum(1 for success in results.values() if success)
    
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Steps: {total_steps}")
    print(f"Successful: {successful_steps}")
    print(f"Failed: {total_steps - successful_steps}")
    print(f"Success Rate: {successful_steps/total_steps*100:.1f}%")
    
    print(f"\nStep Details:")
    step_names = {
        "fetch": "RSS Feed Fetching",
        "process": "Content Processing", 
        "affiliate": "Affiliate Link Addition",
        "html": "HTML Generation"
    }
    
    for step, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        name = step_names.get(step, step)
        print(f"  {status} {name}")
    
    # ファイル生成確認
    print(f"\nGenerated Files:")
    output_files = [
        ("data/rss_raw.json", "RSS Raw Data"),
        ("data/articles_processed.json", "Processed Articles"),
        ("data/articles_with_affiliate.json", "Articles with Affiliate Links"),
        ("output/index.html", "Final HTML Page"),
        ("output/sitemap.json", "Sitemap Data")
    ]
    
    for file_path, description in output_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"  ✅ {description}: {file_path} ({file_size:,} bytes)")
        else:
            print(f"  ❌ {description}: {file_path} (not found)")

def main():
    """メイン処理 - 全パイプラインを実行"""
    print(f"🎯 RSS Affiliate Pipeline Starting...")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    pipeline_start = time.time()
    
    # 前チェック
    if not check_requirements():
        print("❌ Requirements check failed. Exiting.")
        sys.exit(1)
    
    # ディレクトリ準備
    create_directories()
    
    # 古いデータのバックアップ（オプション）
    cleanup_old_data(keep_backups=True)
    
    # パイプライン実行
    pipeline_steps = [
        ("01_fetch_rss.py", "RSS Feed Fetching", "fetch"),
        ("02_process_content.py", "Content Processing & Summarization", "process"),
        ("03_add_affiliate.py", "Affiliate Link Addition", "affiliate"),
        ("04_generate_html.py", "HTML Page Generation", "html")
    ]
    
    results = {}
    
    for script, description, key in pipeline_steps:
        success = run_script(script, description)
        results[key] = success
        
        if not success:
            print(f"❌ Pipeline stopped at: {description}")
            if not DEBUG:
                break
            else:
                print("🐛 DEBUG mode: Continuing despite errors...")
    
    # 実行時間計算
    total_duration = time.time() - pipeline_start
    
    # レポート生成
    generate_report(results)
    
    print(f"\nTotal Pipeline Duration: {total_duration:.1f} seconds")
    
    # 最終ステータス
    all_success = all(results.values())
    if all_success:
        print(f"\n🎉 Pipeline completed successfully!")
        print(f"🌐 Ready for GitHub Pages: output/index.html")
        print(f"🔗 Deploy this to GitHub Pages to go live!")
        sys.exit(0)
    else:
        print(f"\n💥 Pipeline completed with errors!")
        print(f"Check the logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()