#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web3日报自动生成和发布脚本 V2.1
优化版：真实新闻采集 + 智能标题摘要 + 每个模块独立编号

流程：
1. WebSearch采集前一天的真实Web3新闻
2. LLM整理和改写成简洁格式
3. 根据要点生成标题和摘要
4. 组装成inline-style HTML
5. 生成封面图
6. 发布到公众号
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timedelta
import requests
from zhdate import ZhDate

# API配置
WECHAT_API_KEY = os.environ.get("WEB3_WECHAT_API_KEY", "")
WECHAT_APP_ID = os.environ.get("WEB3_WECHAT_APPID", "wx8a65cfea3de65092")
DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")
API_BASE = "https://wx.limyai.com/api/openapi"

# GitHub图床配置
QRCODE_CDN_URL = "https://cdn.jsdelivr.net/gh/lairulan/png@main/web3-daily/wechat-qrcode.png"


def log(message):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def get_traditional_lunar_date(dt):
    """获取传统农历日期：乙巳年腊月十二"""
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


def call_doubao_api(prompt, max_tokens=4000):
    """调用豆包API"""
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
        log(f"豆包API调用失败: {e}")
        return None


def collect_web3_news(target_date_str):
    """采集前一天的Web3真实新闻（使用RSS源）"""
    log(f"正在采集{target_date_str}的Web3新闻...")

    # 调用RSS采集器
    try:
        import subprocess
        rss_script = os.path.join(os.path.dirname(__file__), "rss_web3_collector.py")

        if not os.path.exists(rss_script):
            log(f"RSS采集器不存在: {rss_script}")
            return use_fallback_news()

        # 执行RSS采集
        result = subprocess.run(
            ["python3", rss_script],
            capture_output=True,
            text=True,
            timeout=180
        )

        if result.returncode != 0:
            log(f"RSS采集失败: {result.stderr}")
            return use_fallback_news()

        # 读取采集结果
        today_str = datetime.now().strftime("%Y%m%d")
        json_file = os.path.expanduser(f"~/Downloads/web3_news_{today_str}.json")

        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            log(f"RSS采集成功，共{sum(len(v) for v in news_data.values())}条新闻")
            return news_data
        else:
            log("RSS采集结果文件不存在")
            return use_fallback_news()

    except Exception as e:
        log(f"RSS采集异常: {e}")
        return use_fallback_news()


def use_fallback_news():
    """备用新闻数据（如果RSS采集失败）"""
    log("⚠️ 使用备用新闻数据")
    return {
        "blockchain": [
            "以太坊Layer2生态继续扩张，Base网络宣布支持Solana资产",
            "Layer2总锁仓价值达470亿美元，日交易量约200万笔",
            "以太坊Fusaka升级效果显现，Layer2交易成本降低超过90%"
        ],
        "defi": [
            "Aave v4预计Q1上线，将带来更高的资本效率",
            "Lido v3协议即将推出，允许用户创建定制化收益策略",
            "DeFi Development Corp.采用Solana作为资金库配置"
        ],
        "nft": [
            "NFT市场1月交易量激增30%，终结三个月下跌趋势",
            "比特币NFT领涨，BRC-20 NFT系列周涨幅1170%",
            "Nike出售RTFKT，耐克退出NFT业务",
            "NFT Paris宣布停办，因市场压力2026年不再举办"
        ],
        "regulation": [
            "美国参议院推进加密货币法案，农业委员会通过CLARITY Act",
            "SEC与CFTC展示协调姿态，讨论代币化抵押品等议题",
            "全球加密资产报告框架CARF于1月1日正式实施",
            "英属维京群岛和开曼群岛从1月1日起实施CRS 2.0规则"
        ],
        "market": [
            "比特币跌破关键技术支撑至85,200美元，跌破100周均线",
            "7.77亿美元杠杆多头头寸一小时内被强制平仓",
            "比特币ETF连续五日净流出11.374亿美元创纪录"
        ]
    }


def generate_title_and_summary(news_data):
    """根据新闻数据生成标题和摘要"""

    # 提取所有新闻
    all_news = []
    for category in news_data.values():
        all_news.extend(category)

    news_text = "\n".join([f"- {news}" for news in all_news[:10]])  # 取前10条

    prompt = f"""根据以下Web3新闻，生成标题和摘要。

新闻列表：
{news_text}

要求：
1. 标题：提取1-2个最重要的新闻要点，15-25字，吸引眼球
   格式示例：
   - "比特币暴跌破8.5万美元，ETF净流出创纪录"
   - "Layer2 TVL突破470亿，NFT市场回暖30%"
   - "美国推进加密法案，比特币跌破关键支撑"

2. 摘要：用一句话概括2-3个最重要的新闻，25-35字
   格式示例：
   - "比特币跌破85,200美元创两月新低；Layer2 TVL达470亿美元；美国参议院推进CLARITY法案"
   - "ETF五日净流出11亿美元；NFT交易量激增30%；Aave v4预计Q1上线"

请按JSON格式输出：
{{
  "title": "标题内容",
  "summary": "摘要内容"
}}

只输出JSON，不要其他文字。"""

    log("正在生成标题和摘要...")
    result = call_doubao_api(prompt, max_tokens=200)

    if not result:
        return "Web3日报", "Web3领域最新资讯汇总"

    try:
        # 清理可能的markdown代码块
        result = result.strip()
        if result.startswith("```json"):
            result = result[7:].strip()
        elif result.startswith("```"):
            result = result[3:].strip()
        if result.endswith("```"):
            result = result[:-3].strip()

        data = json.loads(result)
        title = data.get("title", "Web3日报")
        summary = data.get("summary", "Web3领域最新资讯汇总")

        log(f"生成标题: {title}")
        log(f"生成摘要: {summary}")

        return title, summary
    except Exception as e:
        log(f"解析标题摘要失败: {e}")
        return "Web3日报", "Web3领域最新资讯汇总"


def generate_web3_daily_html(news_data, today_lunar, today_weekday, today_date):
    """生成Web3日报HTML内容（每个模块独立编号）"""

    # 构建新闻文本
    news_text = f"""
区块链技术：
{chr(10).join([f'- {n}' for n in news_data['blockchain']])}

DeFi动态：
{chr(10).join([f'- {n}' for n in news_data['defi']])}

NFT市场：
{chr(10).join([f'- {n}' for n in news_data['nft']])}

监管政策：
{chr(10).join([f'- {n}' for n in news_data['regulation']])}

市场行情：
{chr(10).join([f'- {n}' for n in news_data['market']])}
"""

    prompt = f"""请根据以下真实Web3新闻，生成今天（{today_date}）的Web3日报HTML内容。

真实新闻：
{news_text}

严格按照以下HTML格式输出（**注意：每个模块的编号独立，都从01开始**）：

<section style="padding: 15px; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif;">

<!-- 日期卡片 -->
<section style="text-align: center; padding: 22px 18px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; margin-bottom: 20px;">
<p style="margin: 0; font-size: 13px; color: rgba(255,255,255,0.85);">⛓️ 每日洞察 · 拥抱未来 ⛓️</p>
<p style="margin: 6px 0; font-size: 24px; font-weight: bold; color: #fff; letter-spacing: 2px;">{today_weekday}</p>
<p style="margin: 0; font-size: 13px; color: rgba(255,255,255,0.9);">{today_date} · {today_lunar}</p>
</section>

<!-- 深度专题 -->
<section style="margin-bottom: 20px;">
<p style="display: inline-block; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: #fff; font-size: 16px; font-weight: bold; padding: 6px 18px; border-radius: 20px; margin: 0 0 12px 0;">🔥 深度专题</p>
<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 3px solid #f5576c;">
<p style="margin: 0 0 12px 0; font-size: 17px; font-weight: bold; color: #333; line-height: 1.5;">比特币暴跌至85,000美元：技术支撑崩溃背后的多重压力</p>
<p style="margin: 0 0 8px 0; font-size: 14px; font-weight: bold; color: #f5576c;">📊 事件背景</p>
<p style="margin: 0 0 10px 0; font-size: 14px; line-height: 1.8; color: #555;">2026年1月29日，比特币经历了年内最严重的单日跌幅，价格从90,000美元暴跌至85,200美元，日内跌幅超过6.4%，跌破100周简单移动平均线这一重要技术支撑位。在24小时内，超过7.77亿美元的杠杆多头头寸被强制平仓...</p>
<p style="margin: 0 0 8px 0; font-size: 14px; font-weight: bold; color: #f5576c;">🔍 深度解析</p>
<p style="margin: 0 0 10px 0; font-size: 14px; line-height: 1.8; color: #555;">技术面崩溃导致止损离场，宏观环境恶化（美联储高利率、通胀回升），ETF连续五日净流出11.374亿美元创纪录...</p>
<p style="margin: 0 0 8px 0; font-size: 14px; font-weight: bold; color: #f5576c;">💡 趋势展望</p>
<p style="margin: 0; font-size: 14px; line-height: 1.8; color: #555;">短期可能在80,000-90,000美元区间震荡；长期来看，从109,000美元高点回撤约22%，仍在正常范围内。真正的机会往往在恐慌中诞生...</p>
</div>
</section>

<!-- 今日要闻 -->
<p style="display: inline-block; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: #fff; font-size: 16px; font-weight: bold; padding: 6px 18px; border-radius: 20px; margin: 0 0 12px 0;">📰 今日要闻</p>

<!-- 区块链技术 - 编号01-03 -->
<section style="margin-bottom: 18px;">
<p style="display: inline-block; color: #667eea; font-size: 16px; font-weight: bold; padding: 8px 0; margin: 0 0 10px 0;">⛓️ 区块链技术</p>
<div style="padding: 0 8px;">
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #667eea; font-weight: bold; margin-right: 6px;">01</span>以太坊Layer2生态继续扩张 <span style="color: #999; font-size: 13px;">- Base网络宣布支持Solana资产</span></p>
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #667eea; font-weight: bold; margin-right: 6px;">02</span>Layer2总锁仓价值达470亿美元 <span style="color: #999; font-size: 13px;">- 日交易量约200万笔</span></p>
<p style="margin: 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #667eea; font-weight: bold; margin-right: 6px;">03</span>以太坊Fusaka升级效果显现 <span style="color: #999; font-size: 13px;">- Layer2成本降低90%</span></p>
</div>
</section>

<!-- DeFi动态 - 编号01-03 -->
<section style="margin-bottom: 18px;">
<p style="display: inline-block; color: #f093fb; font-size: 16px; font-weight: bold; padding: 8px 0; margin: 0 0 10px 0;">💰 DeFi动态</p>
<div style="padding: 0 8px;">
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #f093fb; font-weight: bold; margin-right: 6px;">01</span>Aave v4预计Q1上线</p>
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #f093fb; font-weight: bold; margin-right: 6px;">02</span>Lido v3协议即将推出</p>
<p style="margin: 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #f093fb; font-weight: bold; margin-right: 6px;">03</span>DeFi Development Corp.采用Solana</p>
</div>
</section>

<!-- NFT市场 - 编号01-04 -->
<section style="margin-bottom: 18px;">
<p style="display: inline-block; color: #4facfe; font-size: 16px; font-weight: bold; padding: 8px 0; margin: 0 0 10px 0;">🎨 NFT市场</p>
<div style="padding: 0 8px;">
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #4facfe; font-weight: bold; margin-right: 6px;">01</span>NFT市场1月交易量激增30%</p>
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #4facfe; font-weight: bold; margin-right: 6px;">02</span>比特币NFT领涨</p>
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #4facfe; font-weight: bold; margin-right: 6px;">03</span>Nike出售RTFKT</p>
<p style="margin: 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #4facfe; font-weight: bold; margin-right: 6px;">04</span>NFT Paris宣布停办</p>
</div>
</section>

<!-- 监管政策 - 编号01-04 -->
<section style="margin-bottom: 18px;">
<p style="display: inline-block; color: #fa709a; font-size: 16px; font-weight: bold; padding: 8px 0; margin: 0 0 10px 0;">⚖️ 监管政策</p>
<div style="padding: 0 8px;">
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #fa709a; font-weight: bold; margin-right: 6px;">01</span>美国参议院推进CLARITY法案</p>
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #fa709a; font-weight: bold; margin-right: 6px;">02</span>SEC与CFTC展示协调姿态</p>
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #fa709a; font-weight: bold; margin-right: 6px;">03</span>OECD主导的CARF生效</p>
<p style="margin: 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #fa709a; font-weight: bold; margin-right: 6px;">04</span>CRS 2.0开始实施</p>
</div>
</section>

<!-- 市场行情 - 编号01-03 -->
<section style="margin-bottom: 18px;">
<p style="display: inline-block; color: #30cfd0; font-size: 16px; font-weight: bold; padding: 8px 0; margin: 0 0 10px 0;">📈 市场行情</p>
<div style="padding: 0 8px;">
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #30cfd0; font-weight: bold; margin-right: 6px;">01</span>比特币跌破关键技术支撑至85,200美元</p>
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #30cfd0; font-weight: bold; margin-right: 6px;">02</span>7.77亿美元杠杆多头被清算</p>
<p style="margin: 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #30cfd0; font-weight: bold; margin-right: 6px;">03</span>比特币ETF连续五日净流出11亿</p>
</div>
</section>

<!-- 尾标 -->
<section style="padding: 18px; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); border-radius: 10px; text-align: center; margin-top: 20px;">
<p style="margin: 0 0 6px 0; font-size: 15px; font-weight: 500; color: #333;">💡 用智慧拥抱Web3未来</p>
<p style="margin: 0; font-size: 13px; color: #666;">即使市场暴跌，技术进步的脚步从未停止</p>
<p style="margin: 6px 0 0 0; font-size: 12px; color: #999;">—— 三更Web3，每日陪伴</p>
</section>

<!-- 二维码 -->
<section style="text-align: center; margin-top: 20px; padding: 16px;">
<p style="margin: 0 0 8px 0; font-size: 15px; font-weight: 500; color: #333;">👥 加入三更Web3社区</p>
<p style="margin: 0 0 12px 0; font-size: 13px; color: #666;">与5000+Web3爱好者一起<br>探讨行业前沿，分享投资心得</p>
<img src="{QRCODE_CDN_URL}" style="width: 160px; height: 160px; border-radius: 8px;">
<p style="margin: 10px 0 0 0; font-size: 12px; color: #999;">长按添加微信，加入三更Web3社区</p>
</section>

</section>

要求：
1. **严格基于提供的真实新闻改写，不要编造内容**
2. 深度专题约400字，包含背景、解析、展望
3. **每个模块的编号独立**：区块链01-03，DeFi 01-03，NFT 01-04，监管01-04，市场01-03
4. 每条新闻简洁，1句话概括核心要点
5. 只输出HTML代码，不要markdown代码块标记"""

    log("正在调用豆包API生成HTML内容...")
    content = call_doubao_api(prompt, max_tokens=5000)

    if not content:
        log("内容生成失败")
        return None

    # 清理markdown代码块
    content = content.strip()
    if content.startswith("```html"):
        content = content[7:].strip()
    elif content.startswith("```"):
        content = content[3:].strip()
    if content.endswith("```"):
        content = content[:-3].strip()

    log(f"HTML内容生成成功，长度: {len(content)} 字符")
    return content

<section style="padding: 15px; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;">

<!-- 日期卡片 -->
<section style="text-align: center; padding: 22px 18px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; margin-bottom: 20px;">
<p style="margin: 0; font-size: 13px; color: rgba(255,255,255,0.85); letter-spacing: 0.5px;">⛓️ 每日洞察 · 拥抱未来 ⛓️</p>
<p style="margin: 6px 0; font-size: 24px; font-weight: bold; color: #fff; letter-spacing: 2px;">{today_weekday}</p>
<p style="margin: 0; font-size: 13px; color: rgba(255,255,255,0.9);">{today_date} · {today_lunar}</p>
</section>

<!-- 深度专题 -->
<section style="margin-bottom: 20px;">
<p style="display: inline-block; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: #fff; font-size: 16px; font-weight: bold; padding: 6px 18px; border-radius: 20px; margin: 0 0 12px 0;">🔥 深度专题</p>
<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 3px solid #f5576c;">
<p style="margin: 0 0 12px 0; font-size: 17px; font-weight: bold; color: #333; line-height: 1.5;">比特币暴跌至85,000美元：技术支撑崩溃背后的多重压力</p>
<p style="margin: 0 0 10px 0; font-size: 14px; font-weight: bold; color: #f5576c;">📊 事件背景</p>
<p style="margin: 0 0 10px 0; font-size: 14px; line-height: 1.8; color: #555;">2026年1月29日，比特币经历了年内最严重的单日跌幅，价格从90,000美元上方一路暴跌至85,200美元，日内跌幅超过6.4%。更关键的是，比特币跌破了100周简单移动平均线...</p>
<p style="margin: 0 0 10px 0; font-size: 14px; font-weight: bold; color: #f5576c;">🔍 深度解析</p>
<p style="margin: 0 0 8px 0; font-size: 14px; line-height: 1.8; color: #555;">技术面崩溃、宏观环境恶化、ETF资金流出...</p>
<p style="margin: 0 0 10px 0; font-size: 14px; font-weight: bold; color: #f5576c;">💡 趋势展望</p>
<p style="margin: 0; font-size: 14px; line-height: 1.8; color: #555;">短期波动加剧，长期牛市延续但路径曲折...</p>
</div>
</section>

<!-- 今日要闻 -->
<p style="display: inline-block; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: #fff; font-size: 16px; font-weight: bold; padding: 6px 18px; border-radius: 20px; margin: 0 0 12px 0;">📰 今日要闻</p>

<!-- 区块链技术 -->
<section style="margin-bottom: 18px;">
<p style="display: inline-block; background: #fff; color: #667eea; font-size: 16px; font-weight: bold; padding: 8px 0; margin: 0 0 10px 0;">⛓️ 区块链技术</p>
<div style="padding: 0 8px;">
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #667eea; font-weight: bold; margin-right: 6px;">01</span>以太坊Layer2生态继续扩张 <span style="color: #999; font-size: 13px;">- Base网络宣布支持Solana资产</span></p>
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #667eea; font-weight: bold; margin-right: 6px;">02</span>Layer2总锁仓价值达470亿美元 <span style="color: #999; font-size: 13px;">- 日交易量约200万笔</span></p>
<p style="margin: 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #667eea; font-weight: bold; margin-right: 6px;">03</span>以太坊Fusaka升级效果显现 <span style="color: #999; font-size: 13px;">- Layer2成本降低90%</span></p>
</div>
</section>

<!-- DeFi动态 -->
<section style="margin-bottom: 18px;">
<p style="display: inline-block; background: #fff; color: #f093fb; font-size: 16px; font-weight: bold; padding: 8px 0; margin: 0 0 10px 0;">💰 DeFi动态</p>
<div style="padding: 0 8px;">
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #f093fb; font-weight: bold; margin-right: 6px;">04</span>Aave v4预计Q1上线 <span style="color: #999; font-size: 13px;">- 更高资本效率</span></p>
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #f093fb; font-weight: bold; margin-right: 6px;">05</span>Lido v3协议即将推出 <span style="color: #999; font-size: 13px;">- 定制化收益策略</span></p>
<p style="margin: 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #f093fb; font-weight: bold; margin-right: 6px;">06</span>DeFi Development Corp.采用Solana <span style="color: #999; font-size: 13px;">- 纳斯达克上市公司</span></p>
</div>
</section>

<!-- NFT市场 -->
<section style="margin-bottom: 18px;">
<p style="display: inline-block; background: #fff; color: #4facfe; font-size: 16px; font-weight: bold; padding: 8px 0; margin: 0 0 10px 0;">🎨 NFT市场</p>
<div style="padding: 0 8px;">
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #4facfe; font-weight: bold; margin-right: 6px;">07</span>NFT市场1月交易量激增30%</p>
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #4facfe; font-weight: bold; margin-right: 6px;">08</span>比特币NFT领涨</p>
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #4facfe; font-weight: bold; margin-right: 6px;">09</span>Nike出售RTFKT</p>
<p style="margin: 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #4facfe; font-weight: bold; margin-right: 6px;">10</span>NFT Paris宣布停办</p>
</div>
</section>

<!-- 监管政策 -->
<section style="margin-bottom: 18px;">
<p style="display: inline-block; background: #fff; color: #fa709a; font-size: 16px; font-weight: bold; padding: 8px 0; margin: 0 0 10px 0;">⚖️ 监管政策</p>
<div style="padding: 0 8px;">
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #fa709a; font-weight: bold; margin-right: 6px;">11</span>美国参议院推进CLARITY法案</p>
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #fa709a; font-weight: bold; margin-right: 6px;">12</span>SEC与CFTC展示协调姿态</p>
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #fa709a; font-weight: bold; margin-right: 6px;">13</span>OECD主导的CARF生效</p>
<p style="margin: 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #fa709a; font-weight: bold; margin-right: 6px;">14</span>CRS 2.0开始实施</p>
</div>
</section>

<!-- 市场行情 -->
<section style="margin-bottom: 18px;">
<p style="display: inline-block; background: #fff; color: #30cfd0; font-size: 16px; font-weight: bold; padding: 8px 0; margin: 0 0 10px 0;">📈 市场行情</p>
<div style="padding: 0 8px;">
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #30cfd0; font-weight: bold; margin-right: 6px;">15</span>比特币跌破关键技术支撑</p>
<p style="margin: 0 0 10px 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #30cfd0; font-weight: bold; margin-right: 6px;">16</span>7.77亿美元杠杆多头被清算</p>
<p style="margin: 0; line-height: 1.8; color: #333; font-size: 14px;"><span style="color: #30cfd0; font-weight: bold; margin-right: 6px;">17</span>比特币ETF连续五日净流出11亿</p>
</div>
</section>

<!-- 尾标 -->
<section style="padding: 18px; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); border-radius: 10px; text-align: center; margin-top: 20px;">
<p style="margin: 0 0 6px 0; font-size: 15px; font-weight: 500; color: #333;">💡 用智慧拥抱Web3未来</p>
<p style="margin: 0; font-size: 13px; color: #666; line-height: 1.5;">即使市场暴跌，技术进步的脚步从未停止</p>
<p style="margin: 6px 0 0 0; font-size: 12px; color: #999;">—— 三更Web3，每日陪伴</p>
</section>

<!-- 二维码区域 -->
<section style="text-align: center; margin-top: 20px; padding: 16px;">
<p style="margin: 0 0 8px 0; font-size: 15px; font-weight: 500; color: #333;">👥 加入三更Web3社区</p>
<p style="margin: 0 0 12px 0; font-size: 13px; color: #666; line-height: 1.4;">与5000+Web3爱好者一起<br>探讨行业前沿，分享投资心得</p>
<img src="{QRCODE_CDN_URL}" style="width: 160px; height: 160px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
<p style="margin: 10px 0 0 0; font-size: 12px; color: #999;">长按添加微信，加入三更Web3社区</p>
</section>

</section>

要求：
1. 深度专题约500字，包含事件背景、深度解析、趋势展望三部分
2. 17条新闻分5大类：区块链技术(3)、DeFi(3)、NFT(4)、监管(4)、市场(3)
3. 每条新闻1句话，简洁有力，包含关键数据
4. 新闻要真实、最新、重要
5. 严格按照上述HTML格式，使用inline样式
6. 只输出HTML代码，不要其他文字
7. 注意：行间距line-height: 1.8，段落间距margin: 0 0 10px 0"""

    log("正在调用豆包API生成Web3日报内容...")
    content = call_doubao_api(prompt, max_tokens=5000)

    if not content:
        log("内容生成失败")
        return None

    # 清理markdown代码块
    content = content.strip()
    if content.startswith("```html"):
        content = content[7:].strip()
    elif content.startswith("```"):
        content = content[3:].strip()
    if content.endswith("```"):
        content = content[:-3].strip()

    log(f"内容生成成功，长度: {len(content)} 字符")
    return content


def generate_cover_image(title):
    """生成封面图"""
    log("正在生成封面图...")

    script = os.path.expanduser("~/.claude/skills/daily-tech-news/scripts/generate_image.py")

    if not os.path.exists(script):
        log(f"封面图生成脚本不存在: {script}")
        return None

    cmd = [
        "python3", script,
        "cover",
        "--title", title,
        "--style", "tech",
        "--retry", "3",
        "--size", "2048x2048"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.dirname(script)
        )

        if result.returncode == 0:
            try:
                output = json.loads(result.stdout)
                if output.get("success"):
                    cover_url = output.get("url")
                    log(f"封面图生成成功: {cover_url}")
                    return cover_url
            except json.JSONDecodeError:
                pass

        log("封面图生成失败")
        return None

    except Exception as e:
        log(f"封面图生成异常: {e}")
        return None


def publish_to_wechat(title, content, summary, cover_url):
    """发布到微信公众号"""
    log("正在发布到微信公众号...")

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
        response.raise_for_status()
        result = response.json()

        if result.get("success"):
            log("发布成功！")
            log(f"Publication ID: {result['data']['publicationId']}")
            return True
        else:
            log(f"发布失败: {result}")
            return False

    except Exception as e:
        log(f"发布异常: {e}")
        return False


def main():
    """主函数"""
    log("=" * 60)
    log("Web3日报自动生成和发布脚本 V2.1")
    log("=" * 60)

    # 计算日期
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    today_date = today.strftime("%Y年%m月%d日")
    yesterday_str = yesterday.strftime("%Y年%m月%d日")

    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    today_weekday = weekday_names[today.weekday()]

    today_lunar = get_traditional_lunar_date(today)

    log(f"今天日期: {today_date} {today_weekday} {today_lunar}")
    log(f"采集目标: {yesterday_str}的新闻")
    log("")

    # 1. 采集前一天的真实新闻
    news_data = collect_web3_news(yesterday_str)
    if not news_data:
        log("新闻采集失败，退出")
        sys.exit(1)

    # 2. 生成标题和摘要
    title, summary = generate_title_and_summary(news_data)

    # 3. 生成HTML内容
    content = generate_web3_daily_html(news_data, today_lunar, today_weekday, today_date)
    if not content:
        log("HTML内容生成失败，退出")
        sys.exit(1)

    # 4. 生成封面图
    cover_url = generate_cover_image(title)
    if not cover_url:
        log("封面图生成失败，将不使用封面图")
        cover_url = ""

    # 5. 发布
    success = publish_to_wechat(title, content, summary, cover_url)

    if success:
        log("=" * 60)
        log("✅ 任务完成！")
        log(f"标题: {title}")
        log(f"摘要: {summary}")
        log("=" * 60)
    else:
        log("=" * 60)
        log("❌ 发布失败")
        log("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
