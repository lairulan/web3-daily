#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web3日报自动生成和发布脚本 V3.0
全新视觉设计版：模板系统 + 专属封面 + 品牌素材

特性：
- 使用新的 HTML 模板系统，支持主题切换
- 专属 Web3 风格封面图生成
- 品牌素材集成
- 更优雅的代码结构
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
import requests

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# 导入模板系统
from html_templates import render_full_page, get_theme, THEMES, preview_theme

# ============================================================
# 配置
# ============================================================

# API 配置 - Web3日报专用
WECHAT_API_KEY = os.environ.get("WEB3_WECHAT_API_KEY", "xhs_fff41080b1861be192872e9cd62399a0")
WECHAT_APP_ID = os.environ.get("WEB3_WECHAT_APPID", "")
DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")
API_BASE = "https://wx.limyai.com/api/openapi"

# CDN URLs
QRCODE_CDN_URL = "https://cdn.jsdelivr.net/gh/lairulan/png@main/web3-daily/wechat-qrcode.png"
# 使用已验证可用的图片作为默认封面
DEFAULT_COVER_URL = "https://cdn.jsdelivr.net/gh/lairulan/png@main/web3-daily/wechat-qrcode.png"

# 默认主题
DEFAULT_THEME = "cyberpunk"

# ============================================================
# 工具函数
# ============================================================

def log(message, level="info"):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️", "progress": "🔄"}
    icon = icons.get(level, "•")
    print(f"[{timestamp}] {icon} {message}")


def get_lunar_date(dt):
    """获取农历日期"""
    try:
        from zhdate import ZhDate
        zh_date = ZhDate.from_datetime(dt)
        chinese_full = zh_date.chinese()
        parts = chinese_full.split()
        gz_year = parts[1] if len(parts) >= 2 else ''

        months = ['', '正月', '二月', '三月', '四月', '五月', '六月',
                  '七月', '八月', '九月', '十月', '冬月', '腊月']
        lunar_month = months[zh_date.lunar_month]

        days = ['', '初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
        lunar_day = days[zh_date.lunar_day]

        return f'{gz_year}{lunar_month}{lunar_day}'
    except Exception as e:
        log(f"获取农历日期失败: {e}", "warning")
        return ""


def call_doubao_api(prompt, max_tokens=4000):
    """调用豆包 API"""
    if not DOUBAO_API_KEY:
        log("未设置 DOUBAO_API_KEY", "error")
        return None

    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

    headers = {
        "Authorization": f"Bearer {DOUBAO_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "doubao-seed-1-6-lite-251015",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        log(f"豆包 API 调用失败: {e}", "error")
        return None


# ============================================================
# 新闻采集
# ============================================================

def collect_web3_news(target_date_str):
    """采集 Web3 新闻（自动翻译成中文）"""
    log(f"正在采集 {target_date_str} 的 Web3 新闻...", "progress")

    # 尝试调用 RSS 采集器（已集成翻译功能）
    try:
        rss_script = os.path.join(SCRIPT_DIR, "rss_web3_collector.py")

        if os.path.exists(rss_script):
            result = subprocess.run(
                ["python3", rss_script],
                capture_output=True,
                text=True,
                timeout=600  # 增加超时，因为需要翻译
            )

            if result.returncode == 0:
                today_str = datetime.now().strftime("%Y%m%d")
                # 优先读取中文翻译版本
                cn_json_file = os.path.expanduser(f"~/Downloads/web3_news_{today_str}_cn.json")
                json_file = os.path.expanduser(f"~/Downloads/web3_news_{today_str}.json")

                target_file = cn_json_file if os.path.exists(cn_json_file) else json_file

                if os.path.exists(target_file):
                    with open(target_file, 'r', encoding='utf-8') as f:
                        news_data = json.load(f)
                    total = sum(len(v) for v in news_data.values())
                    is_chinese = "_cn" in target_file
                    log(f"新闻采集成功，共 {total} 条 ({'中文' if is_chinese else '英文'})", "success")
                    return news_data

    except Exception as e:
        log(f"RSS 采集异常: {e}", "warning")

    # 使用备用数据（中文）
    log("使用备用新闻数据", "warning")
    return get_fallback_news()


def get_fallback_news():
    """备用新闻数据"""
    return {
        "blockchain": [
            {"title": "以太坊 Layer2 生态继续扩张", "detail": "Base 网络宣布支持 Solana 资产"},
            {"title": "Layer2 总锁仓价值达 470 亿美元", "detail": "日交易量约 200 万笔"},
            {"title": "以太坊 Fusaka 升级效果显现", "detail": "Layer2 成本降低 90%"}
        ],
        "defi": [
            {"title": "Aave v4 预计 Q1 上线", "detail": "将带来更高的资本效率"},
            {"title": "Lido v3 协议即将推出", "detail": "允许用户创建定制化收益策略"},
            {"title": "DeFi Development Corp. 采用 Solana", "detail": "纳斯达克上市公司入局"}
        ],
        "nft": [
            {"title": "NFT 市场 1 月交易量激增 30%", "detail": "终结三个月下跌趋势"},
            {"title": "比特币 NFT 领涨", "detail": "BRC-20 NFT 系列周涨幅 1170%"},
            {"title": "Nike 出售 RTFKT", "detail": "耐克退出 NFT 业务"},
            {"title": "NFT Paris 宣布停办", "detail": "因市场压力 2026 年不再举办"}
        ],
        "regulation": [
            {"title": "美国参议院推进加密货币法案", "detail": "农业委员会通过 CLARITY Act"},
            {"title": "SEC 与 CFTC 展示协调姿态", "detail": "讨论代币化抵押品等议题"},
            {"title": "全球加密资产报告框架 CARF 正式实施", "detail": "提高税务透明度"},
            {"title": "英属维京群岛实施 CRS 2.0 规则", "detail": "加强跨境税务合规"}
        ],
        "market": [
            {"title": "比特币跌破关键技术支撑至 85,200 美元", "detail": "跌破 100 周均线"},
            {"title": "7.77 亿美元杠杆多头被清算", "detail": "一小时内强制平仓"},
            {"title": "比特币 ETF 连续五日净流出", "detail": "总额达 11.374 亿美元"}
        ]
    }


# ============================================================
# 内容生成
# ============================================================

def generate_feature_article(news_data):
    """生成深度专题文章（增强版：800-1200字）"""
    # 提取所有新闻
    all_news = []
    for category, items in news_data.items():
        for item in items:
            if isinstance(item, dict):
                all_news.append(f"[{category}] {item.get('title', '')} - {item.get('detail', '')}")
            else:
                all_news.append(f"[{category}] {item}")

    news_text = "\n".join(all_news[:20])

    prompt = f"""你是一位资深的Web3行业分析师。请根据以下今日Web3新闻，选择最重要、最有分析价值的一条新闻，撰写一篇深度专题分析文章。

今日Web3新闻：
{news_text}

请输出JSON格式的深度专题，要求内容丰富、分析深入：

{{
  "title": "专题标题（18-28字，吸引眼球，点明核心要点）",
  "background": "事件背景（200-300字）：详细介绍事件的来龙去脉，包括：1）事件发生的时间、地点、涉及方；2）事件的直接原因；3）相关的历史背景或前情；4）关键数据支撑",
  "analysis": "深度解析（300-400字）：从多个角度分析事件，包括：1）技术层面的影响；2）市场层面的影响；3）行业生态的影响；4）对普通投资者/用户的影响；5）与其他事件的关联性",
  "outlook": "趋势展望（200-300字）：基于分析给出前瞻性判断，包括：1）短期影响（1-2周）；2）中期趋势（1-3个月）；3）长期意义；4）给读者的建议或关注点"
}}

写作要求：
1. 选择今天最重要、最有分析价值的新闻（如重大政策、市场剧烈波动、技术突破等）
2. 分析要有深度和独到见解，不要泛泛而谈
3. 引用新闻中的具体数据来支撑观点
4. 语言专业但通俗易懂，避免过度使用术语
5. 观点客观中立，既指出机会也提示风险
6. 总字数800-1200字
7. 只输出JSON，不要其他文字"""

    log("正在生成深度专题（增强版）...", "progress")
    result = call_doubao_api(prompt, max_tokens=3000)

    if not result:
        return get_fallback_feature()

    try:
        # 清理 markdown
        result = result.strip()
        if result.startswith("```json"):
            result = result[7:].strip()
        elif result.startswith("```"):
            result = result[3:].strip()
        if result.endswith("```"):
            result = result[:-3].strip()

        feature = json.loads(result)

        # 验证内容长度
        total_len = len(feature.get('background', '')) + len(feature.get('analysis', '')) + len(feature.get('outlook', ''))
        if total_len < 400:
            log(f"深度专题内容过短（{total_len}字），使用备用内容", "warning")
            return get_fallback_feature()

        log(f"深度专题生成成功，共 {total_len} 字", "success")
        return feature
    except Exception as e:
        log(f"解析深度专题失败: {e}", "error")
        return get_fallback_feature()


def get_fallback_feature():
    """备用深度专题（当API失败时使用）"""
    return {
        "title": "比特币市场剧烈震荡：清算潮与机构博弈下的多空对决",
        "background": "近期加密货币市场经历了剧烈波动，比特币价格从高位大幅回落，跌破多个关键技术支撑位。这波下跌行情的导火索是多重因素叠加：首先，美联储持续释放鹰派信号，市场对降息预期大幅降温；其次，美国比特币现货ETF连续多日出现净流出，机构资金撤离迹象明显；第三，高杠杆多头仓位在价格下跌过程中被大规模清算，形成连锁反应，加剧了抛售压力。数据显示，仅24小时内就有超过7亿美元的多头仓位被强制平仓，创下近期新高。",
        "analysis": "从技术面来看，比特币跌破100周移动平均线是一个重要的看跌信号，这一支撑位在历史上多次发挥关键作用。从市场情绪来看，恐惧与贪婪指数已跌至\"极度恐惧\"区间，表明市场悲观情绪浓厚。然而，从链上数据来看，长期持有者（LTH）并未出现大规模抛售，说明核心持有者对比特币的长期价值仍有信心。值得关注的是，期货市场的资金费率已转为负值，空头仓位大量累积，这在历史上往往是短期底部的信号之一。此外，机构投资者的动向出现分化：部分传统金融机构选择减仓观望，而一些加密原生机构则开始逢低布局。",
        "outlook": "短期来看，市场可能继续在当前价位附近震荡整理，等待新的催化剂。关键关注点包括：美联储议息会议结果、ETF资金流向变化、以及重要技术支撑位的得失。中期而言，减半效应的滞后影响、机构配置需求、以及监管政策的明朗化将是决定市场方向的关键因素。对于投资者而言，建议保持理性，避免追涨杀跌，可以考虑分批建仓或定投策略来平滑波动风险。同时，关注Layer2、DeFi等赛道的技术创新，这些领域在熊市中往往孕育着下一轮牛市的机会。"
    }


def generate_title_and_summary(news_data, feature):
    """生成文章标题和摘要"""
    all_news = []
    for items in news_data.values():
        for item in items:
            if isinstance(item, dict):
                all_news.append(item.get('title', ''))
            else:
                all_news.append(item)

    news_text = "\n".join([f"- {n}" for n in all_news[:8]])

    prompt = f"""根据以下 Web3 新闻和深度专题，生成公众号文章标题和摘要。

深度专题：{feature.get('title', '')}

新闻要点：
{news_text}

要求：
1. 标题：15-25字，提取1-2个最重要的新闻要点，吸引眼球
2. 摘要：25-40字，概括2-3个核心内容

输出 JSON 格式：
{{
  "title": "标题",
  "summary": "摘要"
}}

只输出 JSON。"""

    result = call_doubao_api(prompt, max_tokens=200)

    if not result:
        return feature.get('title', 'Web3 日报'), "Web3 领域最新资讯汇总"

    try:
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        if result.endswith("```"):
            result = result[:-3]

        data = json.loads(result.strip())
        return data.get("title", "Web3 日报"), data.get("summary", "Web3 领域最新资讯汇总")
    except:
        return feature.get('title', 'Web3 日报'), "Web3 领域最新资讯汇总"


# ============================================================
# 封面图生成
# ============================================================

def generate_cover_image(title, style="cyberpunk"):
    """生成封面图"""
    log(f"正在生成封面图 (风格: {style})...", "progress")

    cover_script = os.path.join(SCRIPT_DIR, "generate_web3_cover_v2.py")

    if not os.path.exists(cover_script):
        log("封面图生成脚本不存在，使用默认封面", "warning")
        return None

    try:
        cmd = [
            "python3", cover_script,
            "--title", title,
            "--style", style,
            "--retry", "3"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=SCRIPT_DIR
        )

        if result.returncode == 0:
            # 查找 JSON 输出
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        data = json.loads(line)
                        if data.get('success'):
                            log(f"封面图生成成功", "success")
                            return data.get('url')
                    except:
                        pass

        log("封面图生成失败", "warning")
        return None

    except Exception as e:
        log(f"封面图生成异常: {e}", "error")
        return None


# ============================================================
# 发布
# ============================================================

def publish_to_wechat(title, content, summary, cover_url):
    """发布到微信公众号"""
    log("正在发布到微信公众号...", "progress")

    url = f"{API_BASE}/wechat-publish"

    headers = {
        "X-API-Key": WECHAT_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "wechatAppid": WECHAT_APP_ID,
        "title": title,
        "content": content,
        "contentFormat": "html",
        "digest": summary,
        "coverImage": cover_url or "",
        "type": "news"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)

        # 获取详细错误信息
        if response.status_code != 200:
            log(f"HTTP状态码: {response.status_code}", "warning")
            try:
                error_detail = response.json()
                log(f"错误详情: {error_detail}", "warning")
            except:
                log(f"响应内容: {response.text[:500]}", "warning")

        response.raise_for_status()
        result = response.json()

        if result.get("success"):
            log("发布成功！", "success")
            pub_id = result.get('data', {}).get('publicationId', 'N/A')
            log(f"Publication ID: {pub_id}", "info")
            return True
        else:
            log(f"发布失败: {result}", "error")
            return False

    except requests.exceptions.HTTPError as e:
        log(f"发布HTTP异常: {e}", "error")
        return False
    except Exception as e:
        log(f"发布异常: {e}", "error")
        return False


def save_to_obsidian(title, content, date_str):
    """保存到 Obsidian"""
    obsidian_dir = os.path.expanduser("~/Documents/Obsidian/Web3日报")
    os.makedirs(obsidian_dir, exist_ok=True)

    filename = f"{date_str.replace('年', '-').replace('月', '-').replace('日', '')}_Web3日报.md"
    filepath = os.path.join(obsidian_dir, filename)

    markdown_content = f"""---
title: {title}
date: {date_str}
tags: [web3, daily, blockchain]
---

# {title}

{content}
"""

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        log(f"已保存到 Obsidian: {filepath}", "success")
        return filepath
    except Exception as e:
        log(f"保存到 Obsidian 失败: {e}", "warning")
        return None


# ============================================================
# 主函数
# ============================================================

def main(theme=None, dry_run=False, cover_style="cyberpunk"):
    """
    主函数

    Args:
        theme: HTML 主题 (cyberpunk/dark_neon/ocean_tech)
        dry_run: 仅生成不发布
        cover_style: 封面风格
    """
    theme = theme or DEFAULT_THEME

    log("=" * 60)
    log("Web3 日报自动生成脚本 V3.0")
    log(f"主题: {theme} | 封面风格: {cover_style}")
    log("=" * 60)
    print()

    # 计算日期
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    today_date = today.strftime("%Y年%m月%d日")
    yesterday_str = yesterday.strftime("%Y年%m月%d日")

    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    today_weekday = weekday_names[today.weekday()]

    today_lunar = get_lunar_date(today)

    log(f"今天日期: {today_date} {today_weekday} {today_lunar}", "info")
    log(f"采集目标: {yesterday_str}", "info")
    print()

    # Step 1: 采集新闻
    news_data = collect_web3_news(yesterday_str)
    if not news_data:
        log("新闻采集失败，退出", "error")
        return False

    # Step 2: 生成深度专题
    feature = generate_feature_article(news_data)
    log(f"深度专题: {feature.get('title', 'N/A')}", "info")

    # Step 3: 生成标题和摘要
    title, summary = generate_title_and_summary(news_data, feature)
    log(f"文章标题: {title}", "info")
    log(f"文章摘要: {summary}", "info")

    # Step 4: 使用模板系统生成 HTML
    log("正在生成 HTML 内容...", "progress")

    page_data = {
        "weekday": today_weekday,
        "date_str": today_date,
        "lunar_str": today_lunar,
        "feature": feature,
        "news": news_data,
        "qrcode_url": QRCODE_CDN_URL,
        "slogan": "用智慧拥抱Web3未来",
        "subtitle": "即使市场波动，技术进步的脚步从未停止"
    }

    content = render_full_page(page_data, theme)
    log(f"HTML 内容生成成功，长度: {len(content)} 字符", "success")

    # Step 5: 生成封面图
    cover_url = generate_cover_image(title, style=cover_style)
    if not cover_url:
        cover_url = DEFAULT_COVER_URL
        log(f"使用默认封面图: {cover_url}", "info")

    # Step 6: 保存到 Obsidian
    save_to_obsidian(title, content, today_date)

    # Step 7: 发布
    if dry_run:
        log("Dry run 模式，跳过发布", "warning")

        # 保存预览文件
        preview_dir = os.path.expanduser("~/Downloads")
        os.makedirs(preview_dir, exist_ok=True)
        preview_path = os.path.join(preview_dir, f"web3_daily_preview_{today.strftime('%Y%m%d')}.html")
        with open(preview_path, 'w', encoding='utf-8') as f:
            f.write(f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>body {{ max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}</style>
</head>
<body>
{content}
</body>
</html>''')
        log(f"预览文件: {preview_path}", "info")
        return True

    success = publish_to_wechat(title, content, summary, cover_url)

    print()
    log("=" * 60)
    if success:
        log("任务完成！", "success")
        log(f"标题: {title}", "info")
    else:
        log("发布失败", "error")
    log("=" * 60)

    return success


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Web3 日报自动生成脚本 V3.0")
    parser.add_argument("--theme", "-t", default="cyberpunk",
                       choices=list(THEMES.keys()),
                       help="HTML 主题")
    parser.add_argument("--cover-style", "-c", default="cyberpunk",
                       choices=["cyberpunk", "neon", "abstract", "minimal", "defi", "nft"],
                       help="封面图风格")
    parser.add_argument("--dry-run", "-d", action="store_true",
                       help="仅生成不发布")
    parser.add_argument("--preview", "-p", action="store_true",
                       help="生成主题预览")

    args = parser.parse_args()

    if args.preview:
        # 预览模式
        test_data = preview_theme(args.theme)
        content = render_full_page(test_data, args.theme)

        preview_path = os.path.expanduser(f"~/Downloads/web3_theme_preview_{args.theme}.html")
        with open(preview_path, 'w', encoding='utf-8') as f:
            f.write(f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Web3日报主题预览 - {args.theme}</title>
<style>body {{ max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}</style>
</head>
<body>
{content}
</body>
</html>''')
        print(f"预览文件已保存: {preview_path}")
    else:
        success = main(
            theme=args.theme,
            dry_run=args.dry_run,
            cover_style=args.cover_style
        )
        sys.exit(0 if success else 1)
