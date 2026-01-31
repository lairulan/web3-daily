#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web3日报RSS新闻采集器 v3.0
- 智能分类：根据关键词精确分配新闻到对应分类
- 市场行情：自动获取BTC/ETH实时价格
- 中文翻译：批量+逐条翻译，多重容错
"""

import os
import sys
import json
import urllib.request
import urllib.error
import ssl
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import re
import time
from email.utils import parsedate_to_datetime
import requests

# SSL配置
try:
    import certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    ssl_context = ssl._create_unverified_context()

# API配置
DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")

# RSS源配置（统一采集，后续智能分类）
RSS_SOURCES = [
    {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "limit": 30},
    {"name": "Cointelegraph", "url": "https://cointelegraph.com/rss", "limit": 30},
    {"name": "Decrypt", "url": "https://decrypt.co/feed", "limit": 20},
]

# 分类关键词配置
CATEGORY_KEYWORDS = {
    "blockchain": {
        "primary": ["ethereum", "eth 2.0", "layer 2", "layer2", "l2", "rollup", "zk-", "zero knowledge",
                   "solana", "cardano", "polkadot", "avalanche", "cosmos", "polygon", "arbitrum",
                   "optimism", "base network", "blockchain", "protocol", "upgrade", "hard fork",
                   "mainnet", "testnet", "validator", "node", "consensus", "proof of"],
        "exclude": ["price", "etf", "sec", "regulation", "defi", "nft", "trading"]
    },
    "defi": {
        "primary": ["defi", "decentralized finance", "aave", "uniswap", "compound", "makerdao",
                   "curve", "lido", "staking", "yield", "liquidity", "lending", "borrowing",
                   "tvl", "total value locked", "dex", "amm", "swap", "pool", "farming",
                   "vault", "dao", "governance token"],
        "exclude": ["nft", "regulation", "sec"]
    },
    "nft": {
        "primary": ["nft", "non-fungible", "opensea", "blur", "ordinals", "brc-20", "inscription",
                   "digital art", "collectible", "metaverse", "gaming", "play-to-earn", "p2e",
                   "pudgy", "bayc", "cryptopunks", "azuki", "doodles", "art blocks"],
        "exclude": ["defi", "regulation", "etf"]
    },
    "regulation": {
        "primary": ["sec", "cftc", "regulation", "regulatory", "compliance", "law", "legal",
                   "court", "lawsuit", "enforcement", "license", "ban", "approval", "congress",
                   "senate", "bill", "act", "framework", "policy", "government", "fed", "central bank",
                   "tax", "mica", "aml", "kyc", "sanction"],
        "exclude": ["price prediction", "trading"]
    },
    "market": {
        "primary": ["bitcoin price", "btc price", "eth price", "ethereum price", "market cap",
                   "trading volume", "bull", "bear", "rally", "crash", "surge", "drop", "plunge",
                   "etf", "spot etf", "futures", "options", "liquidation", "whale", "outflow",
                   "inflow", "all-time high", "ath", "support", "resistance", "prediction"],
        "exclude": []
    }
}

REQUEST_DELAY = 0.5


def log(message, level="info"):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️", "progress": "🔄"}
    icon = icons.get(level, "•")
    print(f"[{timestamp}] {icon} {message}")


def call_doubao_api(prompt, max_tokens=4000, timeout=60):
    """调用豆包API"""
    if not DOUBAO_API_KEY:
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
        "temperature": 0.3
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        log(f"豆包API调用失败: {e}", "error")
        return None


# ============================================================
# 市场行情获取
# ============================================================

def get_crypto_prices() -> Dict:
    """获取BTC和ETH实时价格"""
    log("获取BTC/ETH实时价格...", "progress")

    prices = {"btc": None, "eth": None}

    try:
        # 使用 CoinGecko API（免费，无需API Key）
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum",
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true"
        }

        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()

            if "bitcoin" in data:
                btc = data["bitcoin"]
                prices["btc"] = {
                    "price": btc.get("usd", 0),
                    "change_24h": btc.get("usd_24h_change", 0),
                    "volume_24h": btc.get("usd_24h_vol", 0),
                    "market_cap": btc.get("usd_market_cap", 0)
                }

            if "ethereum" in data:
                eth = data["ethereum"]
                prices["eth"] = {
                    "price": eth.get("usd", 0),
                    "change_24h": eth.get("usd_24h_change", 0),
                    "volume_24h": eth.get("usd_24h_vol", 0),
                    "market_cap": eth.get("usd_market_cap", 0)
                }

            log(f"BTC: ${prices['btc']['price']:,.0f} ({prices['btc']['change_24h']:+.2f}%)", "success")
            log(f"ETH: ${prices['eth']['price']:,.0f} ({prices['eth']['change_24h']:+.2f}%)", "success")

    except Exception as e:
        log(f"获取价格失败: {e}", "warning")

    return prices


def generate_market_news(prices: Dict) -> List[Dict]:
    """根据实时价格生成市场行情新闻"""
    news = []

    if prices.get("btc"):
        btc = prices["btc"]
        price = btc["price"]
        change = btc["change_24h"]
        vol = btc["volume_24h"] / 1e9  # 转换为十亿

        if change > 0:
            trend = "上涨"
            emoji = "📈"
        else:
            trend = "下跌"
            emoji = "📉"

        news.append({
            "title": f"比特币24小时{trend}{abs(change):.1f}%，现报${price:,.0f}",
            "detail": f"24小时交易量{vol:.1f}B美元"
        })

    if prices.get("eth"):
        eth = prices["eth"]
        price = eth["price"]
        change = eth["change_24h"]
        vol = eth["volume_24h"] / 1e9

        if change > 0:
            trend = "上涨"
        else:
            trend = "下跌"

        news.append({
            "title": f"以太坊24小时{trend}{abs(change):.1f}%，现报${price:,.0f}",
            "detail": f"24小时交易量{vol:.1f}B美元"
        })

    # 添加BTC/ETH比率
    if prices.get("btc") and prices.get("eth"):
        ratio = prices["btc"]["price"] / prices["eth"]["price"]
        news.append({
            "title": f"BTC/ETH汇率为{ratio:.1f}，以太坊相对比特币估值分析",
            "detail": "关注两大主流资产的相对强弱表现"
        })

    return news


# ============================================================
# 智能分类
# ============================================================

def classify_news(title: str, description: str = "") -> str:
    """根据关键词智能分类新闻"""
    text = (title + " " + description).lower()

    scores = {}
    for category, config in CATEGORY_KEYWORDS.items():
        score = 0

        # 计算匹配得分
        for keyword in config["primary"]:
            if keyword.lower() in text:
                score += 2

        # 排除词扣分
        for exclude in config.get("exclude", []):
            if exclude.lower() in text:
                score -= 1

        scores[category] = max(0, score)

    # 返回得分最高的分类
    if max(scores.values()) == 0:
        return "blockchain"  # 默认分类

    return max(scores, key=scores.get)


def fetch_and_classify_all_news() -> Dict[str, List[Dict]]:
    """采集所有新闻并智能分类"""
    log("Step 1: 采集RSS新闻...", "progress")

    all_items = []

    for source in RSS_SOURCES:
        log(f"  从 {source['name']} 采集...", "info")
        items = fetch_rss_items(source['url'], source['limit'])
        for item in items:
            item['source'] = source['name']
        all_items.extend(items)
        time.sleep(REQUEST_DELAY)

    log(f"  共采集 {len(all_items)} 条原始新闻", "info")

    # 去重
    seen_titles = set()
    unique_items = []
    for item in all_items:
        title_key = item['title'][:50].lower()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_items.append(item)

    log(f"  去重后 {len(unique_items)} 条", "info")

    # 智能分类
    log("Step 2: 智能分类...", "progress")
    classified = {
        "blockchain": [],
        "defi": [],
        "nft": [],
        "regulation": [],
        "market": []
    }

    for item in unique_items:
        category = classify_news(item['title'], item.get('description', ''))
        item['category'] = category

        # 构建新闻文本
        title = item['title']
        desc = item.get('description', '')
        if desc and len(desc) > 30:
            news_text = f"{title} - {desc[:100]}"
        else:
            news_text = title

        classified[category].append(news_text)

    # 统计
    for cat, items in classified.items():
        log(f"  {cat}: {len(items)} 条", "info")

    return classified


def fetch_rss_items(url: str, limit: int = 20, hours_ago: int = 48) -> List[Dict]:
    """获取RSS条目"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
            content = response.read()

        root = ET.fromstring(content)
        item_elements = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')

        cutoff_time = datetime.now() - timedelta(hours=hours_ago)

        items = []
        for elem in item_elements[:limit * 2]:
            item = {}

            title_elem = elem.find('title')
            if title_elem is None:
                title_elem = elem.find('{http://www.w3.org/2005/Atom}title')

            if title_elem is not None and title_elem.text:
                item['title'] = title_elem.text.strip()
            else:
                continue

            desc_elem = elem.find('description')
            if desc_elem is None:
                desc_elem = elem.find('{http://www.w3.org/2005/Atom}summary')

            if desc_elem is not None and desc_elem.text:
                desc_text = desc_elem.text.strip()
                desc_text = re.sub(r'<[^>]+>', '', desc_text)
                desc_text = re.sub(r'\s+', ' ', desc_text)
                item['description'] = desc_text[:200]
            else:
                item['description'] = ''

            pub_date_elem = elem.find('pubDate')
            if pub_date_elem is None:
                pub_date_elem = elem.find('{http://www.w3.org/2005/Atom}published')

            if pub_date_elem is not None and pub_date_elem.text:
                try:
                    pub_date = parsedate_to_datetime(pub_date_elem.text)
                    item['pub_date'] = pub_date
                    if pub_date >= cutoff_time:
                        items.append(item)
                except:
                    item['pub_date'] = datetime.now()
                    items.append(item)
            else:
                item['pub_date'] = datetime.now()
                items.append(item)

            if len(items) >= limit:
                break

        return items

    except Exception as e:
        log(f"获取RSS失败 ({url}): {e}", "error")
        return []


# ============================================================
# 翻译功能
# ============================================================

def simple_translate(news: str) -> Dict:
    """简单关键词翻译（备用方案）"""
    translations = {
        "Bitcoin": "比特币", "Ethereum": "以太坊", "crypto": "加密货币",
        "blockchain": "区块链", "DeFi": "DeFi", "NFT": "NFT",
        "regulation": "监管", "SEC": "SEC", "ETF": "ETF",
        "liquidation": "清算", "market": "市场", "price": "价格",
        "trading": "交易", "exchange": "交易所", "token": "代币",
        "staking": "质押", "Layer": "Layer", "bull": "牛市",
        "bear": "熊市", "rally": "反弹", "crash": "暴跌",
        "surge": "飙升", "drop": "下跌", "billion": "亿",
        "Hong Kong": "香港", "US": "美国", "Europe": "欧洲",
    }

    title = news.split(" - ")[0] if " - " in news else news
    title = title[:80]

    for en, cn in translations.items():
        title = title.replace(en, cn)

    return {"title": title, "detail": ""}


def translate_news_batch(news_list: List[str], category: str) -> List[Dict]:
    """批量翻译新闻"""
    if not news_list:
        return []

    news_to_translate = news_list[:6]
    news_text = "\n".join([f"{i+1}. {news[:150]}" for i, news in enumerate(news_to_translate)])

    category_names = {
        "blockchain": "区块链技术",
        "defi": "DeFi",
        "nft": "NFT",
        "regulation": "监管政策",
        "market": "市场行情"
    }

    prompt = f"""请将以下{category_names.get(category, category)}领域的英文新闻翻译成中文。

英文新闻：
{news_text}

翻译要求：
1. 翻译准确、专业，符合Web3行业用语
2. 保留重要数据（数字、百分比、金额等）
3. 专业术语保持英文或使用约定俗成的中文翻译
4. 每条新闻翻译成：标题（15-30字）+ 简述（20-40字）

输出JSON数组（只输出JSON，不要其他文字）：
[{{"title":"中文标题","detail":"中文简述"}}]"""

    log(f"正在翻译 {category} 新闻 ({len(news_to_translate)}条)...", "progress")

    for attempt in range(2):
        result = call_doubao_api(prompt, max_tokens=1500, timeout=60)
        if result:
            try:
                result = result.strip()
                if result.startswith("```"):
                    result = result.split("```")[1]
                    if result.startswith("json"):
                        result = result[4:]
                if result.endswith("```"):
                    result = result[:-3]

                translated = json.loads(result.strip())
                if len(translated) >= len(news_to_translate) * 0.5:
                    log(f"{category} 翻译成功，共 {len(translated)} 条", "success")
                    return translated
            except Exception as e:
                log(f"翻译解析失败 (尝试 {attempt+1}): {e}", "warning")
        time.sleep(2)

    # 批量失败，使用简单翻译
    log(f"{category} 翻译失败，使用备用方案", "warning")
    return [simple_translate(news) for news in news_to_translate]


# ============================================================
# 主函数
# ============================================================

def collect_web3_news_chinese(target_date_str: str) -> Dict[str, List[Dict]]:
    """采集所有分类的Web3新闻并翻译成中文"""
    log("=" * 60, "info")
    log(f"Web3新闻采集器 v3.0 (目标日期: {target_date_str})", "info")
    log("=" * 60, "info")

    # Step 1 & 2: 采集并智能分类
    classified_news = fetch_and_classify_all_news()

    # Step 3: 获取市场行情
    prices = get_crypto_prices()
    market_price_news = generate_market_news(prices)

    # Step 4: 翻译各分类
    log("Step 3: 翻译成中文...", "progress")
    result = {}

    for category in ["blockchain", "defi", "nft", "regulation", "market"]:
        news_list = classified_news.get(category, [])

        if category == "market":
            # 市场行情：先加入BTC/ETH价格新闻，再翻译其他
            translated = market_price_news.copy()
            if news_list:
                other_translated = translate_news_batch(news_list[:4], category)
                translated.extend(other_translated)
            result[category] = translated
        else:
            if news_list:
                result[category] = translate_news_batch(news_list, category)
            else:
                result[category] = []

        time.sleep(1)

    # 统计
    log("", "info")
    log("采集+翻译完成！统计:", "success")
    total = 0
    for cat, news in result.items():
        log(f"  {cat}: {len(news)} 条", "info")
        total += len(news)
    log(f"  总计: {total} 条", "info")

    # 保存结果
    output_file = os.path.expanduser(f"~/Downloads/web3_news_{datetime.now().strftime('%Y%m%d')}_cn.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    log(f"中文新闻已保存: {output_file}", "success")

    return result


# 兼容旧接口
def collect_web3_news(target_date_str: str) -> Dict[str, List]:
    return collect_web3_news_chinese(target_date_str)


if __name__ == "__main__":
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y年%m月%d日")

    news_data = collect_web3_news_chinese(yesterday_str)

    print("\n" + "=" * 60)
    print("采集结果预览（中文）:")
    print("=" * 60)

    for category, news_list in news_data.items():
        print(f"\n【{category}】({len(news_list)}条):")
        for i, news in enumerate(news_list[:3], 1):
            if isinstance(news, dict):
                title = news.get('title', '')
                detail = news.get('detail', '')
                print(f"  {i}. {title}")
                if detail:
                    print(f"     {detail}")
            else:
                print(f"  {i}. {news[:80]}...")
