#!/usr/bin/env python3

"""
Open Graph画像生成スクリプト
テクノロジーニュースサイト用のシンプルなOG画像を生成
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_og_image():
    """Open Graph画像を生成"""
    # 画像サイズ (1200x630 推奨)
    width = 1200
    height = 630
    
    # 背景色（テクノロジー感のあるダークブルー）
    bg_color = "#1a1a2e"  # ダークブルー
    accent_color = "#16213e"  # 少し濃いブルー
    text_color = "#ffffff"  # 白
    
    # 画像作成
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # グラデーション風の背景効果
    for i in range(height//3):
        alpha = int(255 * (i / (height//3)) * 0.3)
        color = f"#{hex(26 + alpha//4)[2:].zfill(2)}{hex(26 + alpha//4)[2:].zfill(2)}{hex(46 + alpha//2)[2:].zfill(2)}"
        try:
            draw.rectangle([0, i*3, width, (i+1)*3], fill=color)
        except:
            pass
    
    # デフォルトフォント使用（システムに依存しないよう）
    try:
        # 大きなフォント（タイトル用）
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default() 
        font_small = ImageFont.load_default()
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # テキスト内容
    title = "日本のテックニュース速報"
    subtitle = "2時間ごとに更新される最新IT情報"
    description = "AI・機械学習 | Apple製品 | プログラミング"
    
    # テキスト位置計算
    title_y = height // 3
    subtitle_y = title_y + 80
    desc_y = subtitle_y + 60
    
    # テキスト描画（影効果付き）
    # タイトル
    # 影
    draw.text((52, title_y + 2), title, fill="#000000", font=font_large)
    # 本文
    draw.text((50, title_y), title, fill=text_color, font=font_large)
    
    # サブタイトル
    draw.text((52, subtitle_y + 2), subtitle, fill="#000000", font=font_medium)
    draw.text((50, subtitle_y), subtitle, fill="#e8e8e8", font=font_medium)
    
    # 説明文
    draw.text((52, desc_y + 2), description, fill="#000000", font=font_small)
    draw.text((50, desc_y), description, fill="#b8b8b8", font=font_small)
    
    # 装飾的な要素を追加
    # 右上に小さな四角形
    for i in range(3):
        x = width - 200 + i * 30
        y = 100 + i * 20
        draw.rectangle([x, y, x + 20, y + 20], fill="#4a9eff")
    
    # 右下にテクノロジー感のある線
    for i in range(5):
        y = height - 150 + i * 15
        draw.rectangle([width - 300, y, width - 50, y + 3], fill=f"#4a9e{'ff' if i % 2 == 0 else 'cc'}")
    
    return img

def main():
    """メイン処理"""
    print("🎨 Open Graph画像を生成中...")
    
    try:
        # OG画像生成
        og_image = create_og_image()
        
        # 保存先ディレクトリ
        output_dir = "images"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存
        og_path = os.path.join(output_dir, "og-image.png")
        og_image.save(og_path, "PNG", quality=95)
        
        print(f"✅ Open Graph画像を生成しました: {og_path}")
        print(f"   サイズ: {og_image.size}")
        print(f"   ファイルサイズ: {os.path.getsize(og_path) / 1024:.1f}KB")
        
        # outputとdocsディレクトリにもコピー
        import shutil
        
        for dest_dir in ["output", "docs"]:
            if os.path.exists(dest_dir):
                dest_path = os.path.join(dest_dir, "og-image.png")
                shutil.copy2(og_path, dest_path)
                print(f"✅ {dest_path} にコピーしました")
        
        return True
        
    except Exception as e:
        print(f"❌ 画像生成エラー: {e}")
        return False

if __name__ == "__main__":
    main()