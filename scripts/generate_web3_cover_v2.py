#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web3日报封面图生成器 v2.0
赛博朋克风格，区块链元素，专为 Web3 内容定制

支持多种风格：
- cyberpunk: 赛博朋克（默认）
- neon: 霓虹都市
- abstract: 抽象科技
- minimal: 极简现代
"""

import os
import sys
import json
import subprocess
import time
import urllib.request
import urllib.error
import ssl
import argparse
from datetime import datetime, timedelta

# SSL 配置
ssl_context = ssl._create_unverified_context()

# API 配置
DOUBAO_IMAGE_API_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
DOUBAO_IMAGE_MODEL = "doubao-seedream-4-5-251128"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_IMAGE_MODEL = "google/gemini-2.5-flash-image"
IMGBB_API_URL = "https://api.imgbb.com/1/upload"

# ============================================================
# Web3 封面风格定义
# ============================================================

WEB3_COVER_STYLES = {
    "cyberpunk": {
        "name": "赛博朋克",
        "description": "霓虹灯光、紫蓝渐变、数字矩阵",
        "prompt_elements": [
            "cyberpunk aesthetic",
            "neon purple and blue gradients (#667eea to #764ba2)",
            "cyan neon accents (#00f2fe)",
            "glowing blockchain nodes connected by light beams",
            "digital matrix rain effect",
            "futuristic cityscape silhouette",
            "holographic UI elements",
            "dark background with vibrant neon highlights"
        ],
        "negative_prompt": "text, letters, words, numbers, typography, chinese characters, watermark, signature, blurry, low quality"
    },
    "neon": {
        "name": "霓虹都市",
        "description": "都市夜景、霓虹招牌、未来感",
        "prompt_elements": [
            "neon city nightscape",
            "glowing cryptocurrency symbols floating",
            "Bitcoin, Ethereum logos as neon signs",
            "rain-slicked streets reflecting neon lights",
            "tall buildings with holographic displays",
            "pink and cyan color scheme",
            "synthwave atmosphere",
            "digital billboards showing market charts"
        ],
        "negative_prompt": "text, letters, words, daytime, bright sunlight, realistic people"
    },
    "abstract": {
        "name": "抽象科技",
        "description": "几何形状、流动线条、科技感",
        "prompt_elements": [
            "abstract geometric shapes",
            "flowing digital particles",
            "interconnected nodes forming a network",
            "gradient mesh background purple to blue",
            "3D glass morphism elements",
            "light trails and motion blur",
            "crystalline structures",
            "ethereal glow effects"
        ],
        "negative_prompt": "text, letters, realistic objects, people, faces"
    },
    "minimal": {
        "name": "极简现代",
        "description": "简洁线条、渐变背景、清新感",
        "prompt_elements": [
            "minimalist design",
            "clean gradient background",
            "simple geometric blockchain icon",
            "soft shadows and highlights",
            "modern flat design aesthetic",
            "subtle grid pattern",
            "elegant color transitions",
            "premium magazine cover feel"
        ],
        "negative_prompt": "text, letters, complex details, busy composition, cluttered"
    },
    "defi": {
        "name": "DeFi金融",
        "description": "金融图表、流动性视觉、专业感",
        "prompt_elements": [
            "DeFi protocol visualization",
            "liquidity pool abstract representation",
            "interconnected smart contracts",
            "gold and purple color scheme",
            "financial charts as abstract art",
            "token swap visualization",
            "yield farming concept art",
            "staking rewards visual metaphor"
        ],
        "negative_prompt": "text, numbers, realistic charts, people"
    },
    "nft": {
        "name": "NFT艺术",
        "description": "数字艺术、像素风、收藏品感",
        "prompt_elements": [
            "NFT digital art gallery",
            "floating art frames in virtual space",
            "pixelated elements mixed with smooth gradients",
            "digital ownership concept visualization",
            "collectible art pieces floating",
            "metaverse gallery environment",
            "holographic display frames",
            "artistic blockchain visualization"
        ],
        "negative_prompt": "text, real paintings, copyrighted art, faces"
    }
}

# ============================================================
# 日志工具
# ============================================================

def log(message, level="info"):
    """输出日志"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️", "progress": "🔄"}
    icon = icons.get(level, "•")
    print(f"[{timestamp}] {icon} {message}", file=sys.stderr)


def log_json(data):
    """输出JSON格式日志"""
    print(json.dumps(data, ensure_ascii=False), file=sys.stderr)

# ============================================================
# 图片生成函数
# ============================================================

def build_cover_prompt(title, style="cyberpunk", custom_elements=None):
    """
    构建封面图生成提示词

    Args:
        title: 文章标题（用于主题参考，不会出现在图片中）
        style: 风格名称
        custom_elements: 自定义元素列表

    Returns:
        str: 完整的提示词
    """
    style_config = WEB3_COVER_STYLES.get(style, WEB3_COVER_STYLES["cyberpunk"])

    # 基础元素
    elements = style_config["prompt_elements"].copy()

    # 添加自定义元素
    if custom_elements:
        elements.extend(custom_elements)

    # 根据标题添加主题相关元素
    title_lower = title.lower()
    if any(k in title_lower for k in ["比特币", "bitcoin", "btc", "暴跌", "暴涨", "突破"]):
        elements.append("Bitcoin golden coin prominent in composition")
    elif any(k in title_lower for k in ["以太坊", "ethereum", "eth", "layer2", "l2"]):
        elements.append("Ethereum diamond logo, layer 2 network visualization")
    elif any(k in title_lower for k in ["defi", "流动性", "借贷", "质押"]):
        elements.append("DeFi liquidity visualization, yield farming concept")
    elif any(k in title_lower for k in ["nft", "数字艺术", "收藏"]):
        elements.append("NFT art gallery, digital collectibles floating")
    elif any(k in title_lower for k in ["监管", "政策", "法案", "sec", "合规"]):
        elements.append("regulatory balance scales, official document aesthetic")

    # 构建最终提示词
    prompt = f"""Professional cover image for Web3 daily news.
Theme reference: {title}

Visual elements:
{', '.join(elements)}

Technical requirements:
- Ultra high quality, 8K resolution
- Professional magazine cover composition
- Striking visual impact
- Clean and modern aesthetic
- Perfect for WeChat article thumbnail
- Square format 2048x2048px

IMPORTANT: {style_config['negative_prompt']}
"""

    return prompt


def generate_with_openrouter(prompt, retry=3, retry_delay=5):
    """使用 OpenRouter (Gemini) 生成图片"""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return {"success": False, "error": "未设置 OPENROUTER_API_KEY"}

    last_error = None

    for attempt in range(retry):
        if attempt > 0:
            log(f"OpenRouter 重试 {attempt + 1}/{retry}...", "progress")
            time.sleep(retry_delay)

        try:
            payload = {
                "model": OPENROUTER_IMAGE_MODEL,
                "messages": [{"role": "user", "content": f"Generate an image: {prompt}"}],
                "max_tokens": 4096
            }

            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                OPENROUTER_API_URL,
                data=data,
                headers={
                    'Authorization': f"Bearer {api_key}",
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'https://github.com/lairulan/web3-daily',
                    'X-Title': 'Web3 Daily Cover Generator'
                }
            )

            log("正在调用 OpenRouter API...", "progress")
            with urllib.request.urlopen(req, timeout=180, context=ssl_context) as response:
                result = json.loads(response.read().decode('utf-8'))

            # 提取图片
            choices = result.get('choices', [])
            if choices:
                msg = choices[0].get('message', {})
                images = msg.get('images', [])

                if images:
                    img = images[0]
                    image_url = img.get('image_url', {})
                    if isinstance(image_url, dict):
                        url = image_url.get('url', '')
                    else:
                        url = str(image_url)

                    if url:
                        # Base64 图片需要上传到图床
                        if url.startswith('data:image'):
                            log("图片生成成功，正在上传到图床...", "progress")
                            base64_data = url.split(',')[1] if ',' in url else url
                            upload_result = upload_to_imgbb(base64_data)
                            if upload_result.get('success'):
                                return {
                                    "success": True,
                                    "url": upload_result['url'],
                                    "display_url": upload_result.get('display_url', upload_result['url']),
                                    "source": "openrouter-gemini",
                                    "attempts": attempt + 1
                                }
                            else:
                                last_error = upload_result
                                continue
                        else:
                            return {
                                "success": True,
                                "url": url,
                                "source": "openrouter-gemini",
                                "attempts": attempt + 1
                            }

            last_error = {"success": False, "error": "未能从响应中提取图片", "attempt": attempt + 1}
            log(f"未能提取图片，尝试 {attempt + 1}/{retry}", "warning")

        except urllib.error.URLError as e:
            last_error = {"success": False, "error": f"网络错误: {str(e)}", "attempt": attempt + 1}
            log(f"网络错误: {e}", "error")
        except Exception as e:
            last_error = {"success": False, "error": str(e), "attempt": attempt + 1}
            log(f"异常: {e}", "error")

    return last_error or {"success": False, "error": "所有重试均失败"}


def generate_with_doubao(prompt, retry=3, retry_delay=5, size="2048x2048"):
    """使用豆包 API 生成图片"""
    api_key = os.environ.get("DOUBAO_API_KEY")
    if not api_key:
        return {"success": False, "error": "未设置 DOUBAO_API_KEY"}

    last_error = None

    for attempt in range(retry):
        if attempt > 0:
            log(f"豆包重试 {attempt + 1}/{retry}...", "progress")
            time.sleep(retry_delay)

        try:
            payload = {
                "model": DOUBAO_IMAGE_MODEL,
                "prompt": prompt,
                "response_format": "url",
                "size": size,
                "guidance_scale": 3.5,
                "watermark": False
            }

            log("正在调用豆包 API...", "progress")
            cmd = [
                "curl", "-s", "-X", "POST", DOUBAO_IMAGE_API_URL,
                "-H", f"Authorization: Bearer {api_key}",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(payload, ensure_ascii=False)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            response = json.loads(result.stdout)

            if "error" in response:
                last_error = {
                    "success": False,
                    "error": f"API错误: {response['error'].get('message', str(response['error']))}",
                    "attempt": attempt + 1
                }
                log(f"豆包API错误: {last_error['error']}", "error")
                continue

            if "data" in response and len(response["data"]) > 0:
                image_url = response["data"][0].get("url")
                if image_url:
                    return {
                        "success": True,
                        "url": image_url,
                        "source": "doubao",
                        "attempts": attempt + 1
                    }

            last_error = {"success": False, "error": "未能从响应中提取图片", "attempt": attempt + 1}
            log(f"未能提取图片，尝试 {attempt + 1}/{retry}", "warning")

        except subprocess.TimeoutExpired:
            last_error = {"success": False, "error": "请求超时", "attempt": attempt + 1}
            log("请求超时", "error")
        except Exception as e:
            last_error = {"success": False, "error": str(e), "attempt": attempt + 1}
            log(f"异常: {e}", "error")

    return last_error or {"success": False, "error": "所有重试均失败"}


def upload_to_imgbb(base64_data, retry=2):
    """上传图片到 imgbb 图床"""
    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key:
        return {"success": False, "error": "未设置 IMGBB_API_KEY"}

    import tempfile

    for attempt in range(retry):
        if attempt > 0:
            time.sleep(2)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(base64_data)
            temp_file = f.name

        try:
            cmd = [
                "curl", "-s", "--max-time", "90",
                "-X", "POST",
                f"{IMGBB_API_URL}?key={api_key}",
                "-F", f"image=<{temp_file}"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            response = json.loads(result.stdout)

            if response.get("success"):
                return {
                    "success": True,
                    "url": response["data"]["url"],
                    "display_url": response["data"]["display_url"]
                }
            else:
                log(f"图床上传失败: {response.get('error', {}).get('message', '未知错误')}", "error")

        except Exception as e:
            log(f"图床上传异常: {e}", "error")
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    return {"success": False, "error": "图床上传失败"}


def generate_web3_cover(title, style="cyberpunk", retry=3, size="2048x2048"):
    """
    生成 Web3 封面图（主入口）

    Args:
        title: 文章标题
        style: 风格 (cyberpunk/neon/abstract/minimal/defi/nft)
        retry: 重试次数
        size: 图片尺寸

    Returns:
        dict: {success, url, source, ...}
    """
    log(f"开始生成封面图", "info")
    log(f"  标题: {title}", "info")
    log(f"  风格: {style} ({WEB3_COVER_STYLES.get(style, {}).get('name', '未知')})", "info")

    # 构建提示词
    prompt = build_cover_prompt(title, style)
    log(f"  提示词长度: {len(prompt)} 字符", "info")

    # 优先使用 OpenRouter
    if os.environ.get("OPENROUTER_API_KEY"):
        log("尝试使用 OpenRouter (Gemini)...", "progress")
        result = generate_with_openrouter(prompt, retry=retry)
        if result.get("success"):
            log(f"封面图生成成功！", "success")
            log(f"  URL: {result['url'][:80]}...", "info")
            return result

    # 备用：豆包
    if os.environ.get("DOUBAO_API_KEY"):
        log("尝试使用豆包 API...", "progress")
        result = generate_with_doubao(prompt, retry=retry, size=size)
        if result.get("success"):
            log(f"封面图生成成功！", "success")
            log(f"  URL: {result['url'][:80]}...", "info")
            return result

    log("所有图片生成 API 均失败", "error")
    return {"success": False, "error": "无可用的图片生成 API 或所有尝试均失败"}


# ============================================================
# 命令行入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Web3日报封面图生成器 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
风格选项:
  cyberpunk  赛博朋克（默认）- 霓虹灯光、紫蓝渐变
  neon       霓虹都市 - 都市夜景、未来感
  abstract   抽象科技 - 几何形状、流动线条
  minimal    极简现代 - 简洁线条、清新感
  defi       DeFi金融 - 金融图表、专业感
  nft        NFT艺术 - 数字艺术、像素风

示例:
  python generate_web3_cover_v2.py --title "比特币突破10万美元"
  python generate_web3_cover_v2.py --title "DeFi总TVL新高" --style defi
  python generate_web3_cover_v2.py --date "1月31日"
        """
    )

    parser.add_argument("--title", "-t", type=str, help="文章标题")
    parser.add_argument("--date", "-d", type=str, help="日期（如：1月31日），将自动生成标题")
    parser.add_argument("--style", "-s", default="cyberpunk",
                       choices=list(WEB3_COVER_STYLES.keys()),
                       help="封面风格")
    parser.add_argument("--retry", type=int, default=3, help="重试次数")
    parser.add_argument("--size", default="2048x2048", help="图片尺寸")
    parser.add_argument("--list-styles", action="store_true", help="列出所有可用风格")

    args = parser.parse_args()

    # 列出风格
    if args.list_styles:
        print("\n可用封面风格:\n")
        for key, config in WEB3_COVER_STYLES.items():
            print(f"  {key:12} {config['name']:8} - {config['description']}")
        print()
        return 0

    # 确定标题
    if args.date:
        title = f"{args.date}Web3日报"
    elif args.title:
        title = args.title
    else:
        # 默认使用昨天日期
        yesterday = datetime.now() - timedelta(days=1)
        title = f"{yesterday.month}月{yesterday.day}日Web3日报"

    # 生成封面
    result = generate_web3_cover(
        title=title,
        style=args.style,
        retry=args.retry,
        size=args.size
    )

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
