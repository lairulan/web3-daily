#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三更Web3 品牌素材生成器 v1.0
生成标题栏、尾标等品牌视觉素材

素材规格：
- 标题栏 (title-banner): 900x200px
- 尾标 (footer): 600x150px

风格：赛博朋克科技风，配色与 HTML 模板一致
"""

import os
import sys
import json
import subprocess
import time
import argparse
from datetime import datetime

# API 配置
DOUBAO_IMAGE_API_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
DOUBAO_IMAGE_MODEL = "doubao-seedream-4-5-251128"

# ============================================================
# 品牌素材配置
# ============================================================

BRAND_ASSETS = {
    "title-banner": {
        "name": "标题栏",
        "size": "1792x400",  # 豆包API支持的尺寸，后续可裁剪
        "description": "文章顶部标题栏，展示品牌标识",
        "prompt": """Professional header banner for "三更Web3" (San Geng Web3) brand.

Visual elements:
- Cyberpunk tech aesthetic with gradient purple to blue background (#667eea to #764ba2)
- Neon cyan accents (#00f2fe) as light trails
- Abstract blockchain nodes connected by glowing lines on the left side
- Flowing digital particles and data streams
- Futuristic holographic UI elements
- Dark space background with vibrant neon highlights
- Professional magazine header feel

Composition:
- Wide banner format (4.5:1 aspect ratio)
- Left side: Blockchain network visualization
- Center: Clean space for brand name overlay
- Right side: Subtle crypto symbols (Bitcoin, Ethereum icons as small glowing elements)

Style requirements:
- Ultra high quality, professional design
- Clean modern aesthetic suitable for WeChat article header
- NO text, NO letters, NO words, NO Chinese characters
- Suitable for adding "三更Web3" text overlay later

The design should feel premium, futuristic, and instantly recognizable as a Web3/crypto brand."""
    },

    "footer": {
        "name": "尾标",
        "size": "1200x300",  # 豆包API支持的尺寸
        "description": "文章底部尾标，引导关注",
        "prompt": """Professional footer banner for "三更Web3" brand.

Visual elements:
- Minimalist cyberpunk style
- Soft gradient from warm peach (#ffecd2) to soft coral (#fcb69f)
- Subtle blockchain pattern as watermark
- Small glowing nodes at corners
- Clean, inviting atmosphere
- Professional call-to-action banner feel

Composition:
- Wide banner format (4:1 aspect ratio)
- Center space for text overlay
- Subtle decorative elements at edges
- Warm, approachable yet tech-forward

Style requirements:
- High quality, professional design
- Clean and elegant, not too busy
- NO text, NO letters, NO words
- Suitable for adding "用智慧拥抱Web3未来" text overlay

The design should feel warm and inviting while maintaining tech brand identity."""
    },

    "social-card": {
        "name": "社交卡片",
        "size": "1024x1024",
        "description": "社交媒体分享卡片",
        "prompt": """Social media card for "三更Web3" Web3 daily news brand.

Visual elements:
- Square format for social media
- Cyberpunk gradient background (#667eea to #764ba2)
- Central blockchain network visualization
- Floating cryptocurrency symbols (Bitcoin, Ethereum, etc.)
- Neon glow effects
- Digital particles and light trails

Style requirements:
- Eye-catching for social media feeds
- Professional yet dynamic
- NO text, NO letters, NO numbers
- Suitable for overlaying daily news headlines

Premium quality, visually striking design."""
    },

    "icon": {
        "name": "品牌图标",
        "size": "1024x1024",
        "description": "品牌小图标/头像",
        "prompt": """Brand icon/avatar for "三更Web3" (San Geng Web3).

Visual elements:
- Simple, iconic design
- Blockchain node pattern forming abstract "三" shape
- Gradient purple to blue (#667eea to #764ba2)
- Neon cyan accent (#00f2fe)
- Clean geometric style
- Works well at small sizes

Style requirements:
- Minimalist and memorable
- Recognizable at thumbnail size
- NO text, NO letters
- Professional tech brand feel

Square format, suitable for profile pictures and favicons."""
    }
}

# ============================================================
# 工具函数
# ============================================================

def log(message, level="info"):
    """输出日志"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️", "progress": "🔄"}
    icon = icons.get(level, "•")
    print(f"[{timestamp}] {icon} {message}", file=sys.stderr)


def generate_with_doubao(prompt, size="1024x1024", retry=3):
    """使用豆包 API 生成图片"""
    api_key = os.environ.get("DOUBAO_API_KEY")
    if not api_key:
        return {"success": False, "error": "未设置 DOUBAO_API_KEY"}

    last_error = None

    for attempt in range(retry):
        if attempt > 0:
            log(f"重试 {attempt + 1}/{retry}...", "progress")
            time.sleep(5)

        try:
            payload = {
                "model": DOUBAO_IMAGE_MODEL,
                "prompt": prompt,
                "response_format": "url",
                "size": size,
                "guidance_scale": 3.5,
                "watermark": False
            }

            log(f"调用豆包 API (尺寸: {size})...", "progress")
            cmd = [
                "curl", "-s", "-X", "POST", DOUBAO_IMAGE_API_URL,
                "-H", f"Authorization: Bearer {api_key}",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(payload, ensure_ascii=False)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            response = json.loads(result.stdout)

            if "error" in response:
                last_error = {"success": False, "error": response['error'].get('message', str(response['error']))}
                log(f"API错误: {last_error['error']}", "error")
                continue

            if "data" in response and len(response["data"]) > 0:
                image_url = response["data"][0].get("url")
                if image_url:
                    return {"success": True, "url": image_url, "attempts": attempt + 1}

            last_error = {"success": False, "error": "未能获取图片URL"}
            log("未能获取图片URL", "warning")

        except subprocess.TimeoutExpired:
            last_error = {"success": False, "error": "请求超时"}
            log("请求超时", "error")
        except Exception as e:
            last_error = {"success": False, "error": str(e)}
            log(f"异常: {e}", "error")

    return last_error or {"success": False, "error": "生成失败"}


def download_image(url, save_path):
    """下载图片到本地"""
    try:
        import urllib.request
        import ssl
        ssl_context = ssl._create_unverified_context()

        log(f"下载图片到: {save_path}", "progress")
        urllib.request.urlretrieve(url, save_path)

        if os.path.exists(save_path):
            size = os.path.getsize(save_path)
            log(f"下载成功，文件大小: {size / 1024:.1f} KB", "success")
            return True
        return False
    except Exception as e:
        log(f"下载失败: {e}", "error")
        return False


def generate_brand_asset(asset_type, output_dir=None, retry=3):
    """
    生成品牌素材

    Args:
        asset_type: 素材类型 (title-banner, footer, social-card, icon)
        output_dir: 输出目录
        retry: 重试次数

    Returns:
        dict: {success, url, local_path, ...}
    """
    if asset_type not in BRAND_ASSETS:
        return {"success": False, "error": f"未知素材类型: {asset_type}"}

    config = BRAND_ASSETS[asset_type]
    log(f"开始生成 {config['name']} ({asset_type})", "info")
    log(f"  规格: {config['size']}", "info")

    # 生成图片
    result = generate_with_doubao(
        prompt=config["prompt"],
        size=config["size"],
        retry=retry
    )

    if not result.get("success"):
        return result

    result["asset_type"] = asset_type
    result["asset_name"] = config["name"]

    # 下载到本地
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{asset_type}_{timestamp}.png"
        local_path = os.path.join(output_dir, filename)

        if download_image(result["url"], local_path):
            result["local_path"] = local_path

    log(f"{config['name']} 生成成功！", "success")
    return result


def generate_all_assets(output_dir, retry=3):
    """生成所有品牌素材"""
    results = {}

    for asset_type in ["title-banner", "footer", "icon"]:
        log(f"\n{'='*50}", "info")
        result = generate_brand_asset(asset_type, output_dir, retry)
        results[asset_type] = result

        if not result.get("success"):
            log(f"{asset_type} 生成失败，继续下一个...", "warning")

    return results


# ============================================================
# 命令行入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="三更Web3 品牌素材生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
素材类型:
  title-banner  标题栏 (900x200) - 文章顶部
  footer        尾标 (600x150) - 文章底部
  social-card   社交卡片 (1024x1024) - 分享图
  icon          品牌图标 (512x512) - 头像/favicon
  all           生成所有素材

示例:
  python generate_brand_assets_v2.py title-banner
  python generate_brand_assets_v2.py all --output ./assets
  python generate_brand_assets_v2.py --list
        """
    )

    parser.add_argument("asset_type", nargs="?", default="all",
                       choices=list(BRAND_ASSETS.keys()) + ["all"],
                       help="素材类型")
    parser.add_argument("--output", "-o", type=str,
                       default=os.path.expanduser("~/.claude/skills/web3-daily/assets/brand-materials/generated"),
                       help="输出目录")
    parser.add_argument("--retry", type=int, default=3, help="重试次数")
    parser.add_argument("--list", action="store_true", help="列出所有素材类型")

    args = parser.parse_args()

    # 列出素材类型
    if args.list:
        print("\n可用品牌素材类型:\n")
        for key, config in BRAND_ASSETS.items():
            print(f"  {key:15} {config['name']:8} ({config['size']}) - {config['description']}")
        print()
        return 0

    print("=" * 60)
    print("三更Web3 品牌素材生成器 v1.0")
    print("=" * 60)
    print()

    # 生成素材
    if args.asset_type == "all":
        results = generate_all_assets(args.output, args.retry)
        print("\n" + "=" * 60)
        print("生成结果汇总:")
        print("=" * 60)
        for asset_type, result in results.items():
            status = "✅" if result.get("success") else "❌"
            print(f"  {status} {asset_type}: {result.get('local_path', result.get('error', 'N/A'))}")
    else:
        result = generate_brand_asset(args.asset_type, args.output, args.retry)
        print("\n" + json.dumps(result, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
