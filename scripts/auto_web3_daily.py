#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web3日报自动生成与发布系统
每日采集中英文Web3资讯，生成混合形式内容（热点要闻+深度专题），发布到微信公众号
"""

import os
import sys
import json
import requests
import argparse
from datetime import datetime, timedelta
from zhdate import ZhDate
import re

# API配置
WECHAT_API_KEY = os.environ.get('WECHAT_API_KEY', 'xhs_fff41080b1861be192872e9cd62399a0')
WECHAT_APP_ID = os.environ.get('WEB3_WECHAT_APPID', 'wx8a65cfea3de65092')
DOUBAO_API_KEY = os.environ.get('DOUBAO_API_KEY', '')

# 文件路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(SKILL_DIR, 'assets')
OBSIDIAN_DIR = os.path.expanduser('~/Documents/Obsidian/Web3日报/')

def check_environment():
    """环境依赖预检查"""
    print("🔍 环境依赖检查...")

    issues = []

    # 检查必需的环境变量
    else:
        print("✅ AI API密钥已配置")

    # 检查输出目录
    if not os.path.exists(OBSIDIAN_DIR):
        try:
            os.makedirs(OBSIDIAN_DIR, exist_ok=True)
            print(f"✅ 创建输出目录: {OBSIDIAN_DIR}")
        except Exception as e:
            issues.append(f"❌ 无法创建输出目录: {e}")
    else:
        print(f"✅ 输出目录存在: {OBSIDIAN_DIR}")

    # 检查脚本文件
    required_scripts = ['generate_image.py']
    for script in required_scripts:
        script_path = os.path.join(SCRIPT_DIR, script)
        if not os.path.exists(script_path):
            issues.append(f"❌ 缺少脚本: {script}")
        else:
            print(f"✅ 脚本存在: {script}")

    if issues:
        print("\n⚠️  发现以下问题：")
        for issue in issues:
            print(f"  {issue}")
        return False

    print("\n✅ 环境检查通过！\n")
    return True

def call_ai_api(prompt, model="doubao"):
    """调用AI API"""
        url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "model": "google/gemini-2.0-flash-001:free",
            "messages": [{"role": "user", "content": prompt}]
        }
    elif DOUBAO_API_KEY:
        url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        headers = {
            "Authorization": f"Bearer {DOUBAO_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "ep-20241218161259-vp9lh",
            "messages": [{"role": "user", "content": prompt}]
        }
    else:
        return None

    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ AI API调用失败: {e}")
        return None

def search_web3_news(yesterday_date):
    """搜集Web3资讯"""
    print(f"📰 搜集 {yesterday_date} 的Web3资讯...")

    # 这里使用WebSearch工具，实际运行时由Claude调用
    # 返回格式为资讯列表
    prompt = f"""请搜集 {yesterday_date} 的Web3领域资讯，包括：

1. 区块链技术（以太坊、比特币、Layer2等）
2. DeFi（去中心化金融）
3. NFT/元宇宙
4. 加密货币市场
5. Web3监管政策

搜索中英文媒体，包括：
- 中文：律动BlockBeats、PANews、金色财经、Odaily
- 英文：CoinDesk、The Block、Decrypt、CoinTelegraph

要求：
- 筛选出15-20条重要资讯
- 英文资讯翻译成中文
- 保留DeFi、NFT、DAO等专业术语
- 格式：[分类] 标题 - 简要说明（1句话）

返回JSON格式：
{{
  "news": [
    {{"category": "DeFi", "title": "...", "summary": "...", "source": "..."}},
    ...
  ]
}}
"""

    # 实际应该调用WebSearch，这里简化为AI生成
    return None  # 需要外部WebSearch结果

def select_hot_topic(news_list):
    """从资讯中选择热门话题作为深度专题"""
    print("🔥 分析热门话题，选择深度专题...")

    prompt = f"""基于以下Web3资讯，选择一个最有价值的话题作为深度专题：

资讯列表：
{json.dumps(news_list, ensure_ascii=False, indent=2)}

选择标准：
1. 热度高、影响大
2. 有足够信息支撑深度分析
3. 对Web3行业有重要意义
4. 能展开800-1200字的分析

返回JSON格式：
{{
  "topic": "选定的话题",
  "reason": "选择原因",
  "keywords": ["关键词1", "关键词2"]
}}
"""

    result = call_ai_api(prompt)
    if result:
        try:
            return json.loads(result)
        except:
            return None
    return None

def generate_deep_article(topic_info, news_context):
    """生成深度专题文章（800-1200字）"""
    print(f"✍️  生成深度专题: {topic_info['topic']}")

    prompt = f"""基于以下信息，撰写一篇800-1200字的Web3深度专题文章：

主题：{topic_info['topic']}
背景资讯：{json.dumps(news_context, ensure_ascii=False, indent=2)}

文章结构：
## {topic_info['topic']}

### 📊 事件背景
（200-300字，介绍事件发生的背景和重要性）

### 🔍 深度解析
（400-500字，深入分析技术原理、市场影响、行业意义）

### 💡 趋势展望
（200-300字，分析未来发展方向和对行业的影响）

写作要求：
1. 专业但易懂，面向对Web3有基础了解的读者
2. 使用数据和案例支撑观点
3. DeFi、NFT、Layer2等术语保留英文
4. 项目名称保留英文，必要时括号注中文
5. 客观中立，有独到见解
6. 格式为Markdown

直接返回文章内容，不要额外说明。
"""

    article = call_ai_api(prompt)
    return article if article else "（深度专题生成失败）"

def get_qrcode_url():
    """获取二维码URL（自动上传到图床）"""
    # 本地二维码路径
    qrcode_path = os.path.join(SKILL_DIR, 'assets/brand-materials/qrcode/wechat-qrcode.png')

    # 缓存文件路径（避免重复上传）
    cache_file = os.path.join(SKILL_DIR, 'assets/brand-materials/qrcode/.qrcode-url-cache.txt')

    # 如果缓存存在，直接返回
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cached_url = f.read().strip()
            if cached_url:
                print(f"✅ 使用缓存的二维码URL")
                return cached_url
        except:
            pass

    # 如果本地二维码不存在，返回None使用占位符
    if not os.path.exists(qrcode_path):
        print(f"⚠️  二维码文件不存在: {qrcode_path}")
        print(f"   将使用占位符。请将二维码保存到上述路径。")
        return None

    # 上传二维码到图床
    print(f"📤 上传二维码到图床...")
    upload_script = os.path.join(SCRIPT_DIR, 'upload_image.py')

    try:
        import subprocess
        result = subprocess.run(
            ['python3', upload_script, qrcode_path, 'web3-qrcode'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            # 从输出中提取URL
            output = result.stdout
            for line in output.split('\n'):
                if line.startswith('📸 图片URL:'):
                    url = line.split('📸 图片URL:')[1].strip()
                    # 保存到缓存
                    try:
                        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                        with open(cache_file, 'w') as f:
                            f.write(url)
                    except:
                        pass
                    print(f"✅ 二维码上传成功")
                    return url

        print(f"⚠️  二维码上传失败，将使用占位符")
        return None

    except Exception as e:
        print(f"⚠️  二维码上传异常: {e}")
        return None

def format_news_html(news_list, deep_article, date_str):
    """格式化为HTML内容"""
    # 获取日期信息
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    zh_date = ZhDate.from_datetime(date_obj)
    weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date_obj.weekday()]

    lunar_str = f"{zh_date.chinese()}"
    date_display = f"{date_obj.month}月{date_obj.day}日"

    # 按分类整理资讯
    categories = {
        '区块链技术': [],
        'DeFi动态': [],
        'NFT市场': [],
        '监管政策': [],
        '市场行情': []
    }

    for news in news_list[:15]:  # 最多15条
        category = news.get('category', '其他')
        # 映射到预定义分类
        if 'DeFi' in category or '金融' in category:
            categories['DeFi动态'].append(news)
        elif 'NFT' in category or '元宇宙' in category:
            categories['NFT市场'].append(news)
        elif '监管' in category or '政策' in category:
            categories['监管政策'].append(news)
        elif '行情' in category or '市场' in category:
            categories['市场行情'].append(news)
        else:
            categories['区块链技术'].append(news)

    # 生成HTML
    html = f"""<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">

<!-- 品牌标题栏 -->
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px 20px; border-radius: 12px; text-align: center; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3); position: relative; overflow: hidden;">
    <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(circle at 20% 50%, rgba(0, 242, 254, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 50%, rgba(0, 242, 254, 0.1) 0%, transparent 50%); pointer-events: none;"></div>
    <div style="position: relative; z-index: 1;">
        <div style="font-size: 32px; font-weight: bold; color: white; margin-bottom: 8px; text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2); letter-spacing: 2px;">三更Web3</div>
        <div style="font-size: 14px; color: rgba(255, 255, 255, 0.9); letter-spacing: 1px; font-weight: 300;">⛓️ 每日洞察 · 拥抱未来 ⛓️</div>
    </div>
</div>

<!-- 日期卡片 -->
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 30px;">
  <div style="font-size: 28px; font-weight: bold; margin-bottom: 8px;">{date_display} Web3日报</div>
  <div style="font-size: 16px; opacity: 0.95;">{lunar_str} {weekday}</div>
</div>

<!-- 深度专题 -->
<div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 4px 12px; border-radius: 20px; display: inline-block; margin-bottom: 15px; font-weight: bold;">
  🔥 深度专题
</div>

<div style="background: #f8f9fa; padding: 20px; border-radius: 12px; margin-bottom: 30px; border-left: 4px solid #f5576c;">
{deep_article}
</div>

<!-- 热点要闻 -->
<div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 4px 12px; border-radius: 20px; display: inline-block; margin-bottom: 15px; font-weight: bold;">
  📰 今日要闻
</div>

"""

    # 添加分类资讯
    category_colors = {
        '区块链技术': '#667eea',
        'DeFi动态': '#f093fb',
        'NFT市场': '#4facfe',
        '监管政策': '#fa709a',
        '市场行情': '#30cfd0'
    }

    category_icons = {
        '区块链技术': '⛓️',
        'DeFi动态': '💰',
        'NFT市场': '🎨',
        '监管政策': '⚖️',
        '市场行情': '📈'
    }

    for cat_name, news_items in categories.items():
        if news_items:
            color = category_colors.get(cat_name, '#667eea')
            icon = category_icons.get(cat_name, '📌')

            html += f"""
<div style="margin-top: 25px; margin-bottom: 20px;">
  <div style="font-size: 20px; font-weight: bold; color: {color}; margin-bottom: 12px;">
    {icon} {cat_name}
  </div>
"""

            for idx, news in enumerate(news_items[:5], 1):
                title = news.get('title', '')
                summary = news.get('summary', '')
                source = news.get('source', '')

                html += f"""
  <div style="margin-bottom: 12px; padding-left: 10px; border-left: 3px solid {color};">
    <span style="color: {color}; font-weight: bold; margin-right: 8px;">{idx:02d}.</span>
    <span style="font-weight: 500;">{title}</span>
    {f'<span style="color: #666; font-size: 14px;"> - {summary}</span>' if summary else ''}
    {f'<span style="color: #999; font-size: 12px; margin-left: 8px;">({source})</span>' if source else ''}
  </div>
"""

            html += "</div>\n"

    # 获取二维码URL
    qrcode_url = get_qrcode_url()

    # 结尾尾标
    html += """
<!-- 尾标 -->
<div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 20px; border-radius: 12px; text-align: center; margin-top: 40px; margin-bottom: 30px; font-style: italic; color: #333; box-shadow: 0 4px 12px rgba(252, 182, 159, 0.3);">
    <div style="font-size: 18px; margin-bottom: 8px;">💡</div>
    <div style="font-size: 16px; font-weight: 500; line-height: 1.6;">用智慧拥抱Web3未来</div>
    <div style="font-size: 13px; color: #666; margin-top: 8px; font-style: normal;">—— 三更Web3，每日陪伴</div>
</div>

<!-- 二维码区域 -->
<div style="text-align: center; margin-top: 40px; padding: 30px 20px;">
    <div style="font-size: 18px; font-weight: 500; color: #333; margin-bottom: 15px;">📱 关注三更Web3</div>
    <div style="font-size: 14px; color: #666; margin-bottom: 20px;">每日洞察区块链前沿动态</div>
    <div style="display: inline-block; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #00f2fe 100%); border-radius: 16px; box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);">
        <div style="background: white; padding: 10px; border-radius: 10px;">
"""

    # 根据是否有二维码URL决定显示内容
    if qrcode_url:
        html += f"""
            <img src="{qrcode_url}" alt="三更Web3公众号" style="width: 200px; height: 200px; display: block; border-radius: 8px;">
"""
    else:
        html += """
            <div style="width: 200px; height: 200px; background: #f5f5f5; display: flex; align-items: center; justify-content: center; font-size: 14px; color: #999; border-radius: 8px; text-align: center; line-height: 1.6;">
                请将二维码保存到<br>~/.claude/skills/web3-daily/<br>assets/brand-materials/qrcode/<br>wechat-qrcode.png
            </div>
"""

    html += """
        </div>
    </div>
    <div style="font-size: 12px; color: #999; margin-top: 15px;">长按识别二维码关注</div>
</div>

</div>
"""

    return html

def generate_cover_image(title, date_str):
    """生成封面图"""
    print("🎨 生成封面图...")

    script_path = os.path.join(SCRIPT_DIR, 'generate_image.py')
    if not os.path.exists(script_path):
        print("⚠️  generate_image.py 不存在，跳过封面图生成")
        return None

    import subprocess

    try:
        cmd = [
            'python3', script_path, 'cover',
            '--title', title,
            '--style', 'tech',
            '--size', '2048x2048',
            '--output', os.path.join(OBSIDIAN_DIR, 'images', f'{date_str}-cover.png')
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ 封面图生成成功")
            return os.path.join(OBSIDIAN_DIR, 'images', f'{date_str}-cover.png')
        else:
            print(f"⚠️  封面图生成失败: {result.stderr}")
            return None
    except Exception as e:
        print(f"⚠️  封面图生成异常: {e}")
        return None

def save_to_obsidian(title, content, date_str, word_count):
    """保存到Obsidian"""
    filename = f"{date_str}_{title}.md"
    filepath = os.path.join(OBSIDIAN_DIR, filename)

    frontmatter = f"""---
title: {title}
date: {date_str}
type: Web3日报
word_count: {word_count}
tags: [Web3, 区块链, DeFi, NFT]
---

"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)

    print(f"💾 文章已保存: {filepath}")
    return filepath

def publish_to_wechat(title, html_content, summary, cover_image=None):
    """发布到微信公众号"""
    print("📤 发布到微信公众号...")

    url = "https://wlllb.com/api/wx/article"

    data = {
        "appid": WECHAT_APP_ID,
        "title": title,
        "content": html_content,
        "digest": summary,
        "contentFormat": "html",
        "type": "news"
    }

    # 如果有封面图，上传并添加
    if cover_image and os.path.exists(cover_image):
        # TODO: 实现图片上传逻辑
        pass

    headers = {
        "X-API-KEY": WECHAT_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        if result.get('success'):
            print("✅ 发布成功！")
            return True
        else:
            print(f"❌ 发布失败: {result.get('message')}")
            return False
    except Exception as e:
        print(f"❌ 发布异常: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Web3日报自动生成与发布')
    parser.add_argument('--check-env', action='store_true', help='仅检查环境依赖')
    parser.add_argument('--dry-run', action='store_true', help='试运行，不发布')
    parser.add_argument('--date', type=str, help='指定日期(YYYY-MM-DD)，默认为昨天')

    args = parser.parse_args()

    # 环境检查
    if not check_environment():
        sys.exit(1)

    if args.check_env:
        sys.exit(0)

    # 确定日期
    if args.date:
        target_date = args.date
    else:
        yesterday = datetime.now() - timedelta(days=1)
        target_date = yesterday.strftime('%Y-%m-%d')

    print(f"📅 目标日期: {target_date}\n")

    # 主流程
    print("=" * 60)
    print("🚀 Web3日报生成流程开始")
    print("=" * 60)

    # 注意：实际的新闻采集需要在Claude环境中通过WebSearch完成
    # 这里的脚本主要用于后续处理和发布

    print("\n⚠️  此脚本需要配合Claude的WebSearch功能使用")
    print("请在Claude中运行 web3-daily 技能来完成完整流程\n")

    return 0

if __name__ == '__main__':
    main()
