#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成三更Web3品牌素材
使用豆包SeeDream API生成标题栏、尾标、二维码框
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
import ssl

# 创建 SSL 上下文
ssl_context = ssl._create_unverified_context()

# API 配置
DOUBAO_IMAGE_API_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
DOUBAO_IMAGE_MODEL = "doubao-seedream-4-5-251128"
DOUBAO_API_KEY = os.environ.get('DOUBAO_API_KEY', '')

# 品牌素材配置
BRAND_MATERIALS = {
    'title-banner': {
        'prompt': '''Title banner design for "三更Web3·每日洞察" (San Geng Web3 Daily Insights).
Cyberpunk tech style, futuristic aesthetic, professional branding.
Layout: horizontal banner 900x200 pixels.
Left side: "三更Web3" logo text in modern sans-serif font, glowing effect.
Right side: blockchain network visualization with connected nodes, data streams.
Background: gradient from deep purple (#667eea) to violet (#764ba2), dark tech atmosphere.
Accent colors: neon cyan (#00f2fe), electric blue highlights.
Elements: flowing digital particles, hexagonal patterns, subtle grid overlay.
Style: high-tech, clean composition, suitable for article header.
Chinese and English text blend naturally.
Professional, modern, Web3 themed.''',
        'size': '1024x1024',  # 会被裁剪为 900x200
        'filename': 'web3-title-banner.png'
    },
    'footer': {
        'prompt': '''Footer banner design for Web3 publication.
Text: "用智慧拥抱Web3未来" (Embrace Web3 Future with Wisdom).
Minimalist modern style, inspirational tone.
Layout: horizontal banner 600x150 pixels.
Center: Chinese slogan in elegant font.
Background: soft gradient purple to blue, subtle glow.
Elements: small blockchain icon, abstract geometric shapes.
Style: clean, professional, motivational.
Colors: gradient from #f093fb to #f5576c, soft lighting.
Suitable for article footer/closing.''',
        'size': '1024x1024',  # 会被裁剪为 600x150
        'filename': 'web3-footer.png'
    },
    'qrcode-frame': {
        'prompt': '''QR code frame design for WeChat public account.
Square format 500x500 pixels with center area reserved for QR code.
Outer frame: gradient border from purple (#667eea) to cyan (#00f2fe), tech style.
Bottom text area: "关注三更Web3，每日洞察区块链" (Follow San Geng Web3, Daily Blockchain Insights).
Background: subtle tech pattern, hexagonal grid, blockchain nodes.
Style: modern, professional, tech-themed.
Center 300x300px area should be blank white for QR code placement.
Frame width: 40-50px gradient border.
Colors: purple, blue, cyan gradient, high-tech aesthetic.''',
        'size': '1024x1024',
        'filename': 'web3-qrcode-frame.png'
    }
}

def log_message(message):
    """输出日志"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def generate_image_doubao(prompt, size="1024x1024"):
    """使用豆包API生成图片"""
    if not DOUBAO_API_KEY:
        log_message("❌ 未设置 DOUBAO_API_KEY 环境变量")
        return None

    payload = {
        "model": DOUBAO_IMAGE_MODEL,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "response_format": "url"
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            DOUBAO_IMAGE_API_URL,
            data=data,
            headers={
                'Authorization': f"Bearer {DOUBAO_API_KEY}",
                'Content-Type': 'application/json'
            }
        )

        with urllib.request.urlopen(req, timeout=180, context=ssl_context) as response:
            result = json.loads(response.read().decode('utf-8'))

        # 提取图片URL
        if result.get('data'):
            image_url = result['data'][0].get('url')
            if image_url:
                return image_url

        log_message("❌ 未能从响应中提取图片URL")
        return None

    except urllib.error.URLError as e:
        log_message(f"❌ 网络错误: {str(e)}")
        return None
    except Exception as e:
        log_message(f"❌ 生成失败: {str(e)}")
        return None

def download_image(url, filepath):
    """下载图片到本地"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60, context=ssl_context) as response:
            data = response.read()

        with open(filepath, 'wb') as f:
            f.write(data)

        log_message(f"✅ 图片已保存: {filepath}")
        return True
    except Exception as e:
        log_message(f"❌ 下载失败: {str(e)}")
        return False

def main():
    """主函数"""
    log_message("🎨 开始生成三更Web3品牌素材...")

    # 检查API Key
    if not DOUBAO_API_KEY:
        log_message("❌ 请设置 DOUBAO_API_KEY 环境变量")
        sys.exit(1)

    # 创建输出目录
    output_dir = os.path.expanduser("~/Documents/Obsidian/Web3日报/images/brand")
    os.makedirs(output_dir, exist_ok=True)
    log_message(f"📁 输出目录: {output_dir}")

    # 生成每个素材
    for material_name, config in BRAND_MATERIALS.items():
        log_message(f"\n🖼️  正在生成: {material_name}")
        log_message(f"提示词: {config['prompt'][:100]}...")

        # 调用API生成图片
        image_url = generate_image_doubao(config['prompt'], config['size'])

        if image_url:
            log_message(f"✅ 图片生成成功: {image_url[:60]}...")

            # 下载图片
            filepath = os.path.join(output_dir, config['filename'])
            if download_image(image_url, filepath):
                log_message(f"✅ {material_name} 完成")
            else:
                log_message(f"❌ {material_name} 下载失败")
        else:
            log_message(f"❌ {material_name} 生成失败")

        # 避免API限流
        time.sleep(3)

    log_message("\n" + "="*60)
    log_message("🎉 品牌素材生成完成！")
    log_message(f"📂 文件位置: {output_dir}")
    log_message("="*60)

    # 列出生成的文件
    log_message("\n生成的文件：")
    for material_name, config in BRAND_MATERIALS.items():
        filepath = os.path.join(output_dir, config['filename'])
        if os.path.exists(filepath):
            size_kb = os.path.getsize(filepath) / 1024
            log_message(f"  ✅ {config['filename']} ({size_kb:.1f} KB)")
        else:
            log_message(f"  ❌ {config['filename']} (未生成)")

    log_message("\n📝 后续步骤：")
    log_message("1. 检查生成的图片质量")
    log_message("2. 如需调整，可以修改prompt后重新运行")
    log_message("3. 标题栏和尾标可能需要裁剪到合适尺寸")
    log_message("4. 二维码框需要在中心位置叠加实际二维码")

if __name__ == '__main__':
    main()
