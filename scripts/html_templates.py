#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web3日报 HTML 模板系统 v1.0
支持主题切换、组件复用、样式统一管理
"""

# ============================================================
# 主题配色方案
# ============================================================

THEMES = {
    "cyberpunk": {
        "name": "赛博朋克",
        "primary_gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "secondary_gradient": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "accent_gradient": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "warm_gradient": "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
        "colors": {
            "blockchain": "#667eea",
            "defi": "#f093fb",
            "nft": "#4facfe",
            "regulation": "#fa709a",
            "market": "#30cfd0",
            "feature": "#f5576c",
        },
        "bg_primary": "#f8f9fa",
        "bg_card": "#ffffff",
        "text_primary": "#333333",
        "text_secondary": "#555555",
        "text_muted": "#999999",
    },
    "dark_neon": {
        "name": "暗夜霓虹",
        "primary_gradient": "linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)",
        "secondary_gradient": "linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%)",
        "accent_gradient": "linear-gradient(135deg, #ff00cc 0%, #333399 100%)",
        "warm_gradient": "linear-gradient(135deg, #434343 0%, #000000 100%)",
        "colors": {
            "blockchain": "#00d2ff",
            "defi": "#ff00cc",
            "nft": "#00ff88",
            "regulation": "#ff6b6b",
            "market": "#ffd700",
            "feature": "#ff1493",
        },
        "bg_primary": "#1a1a2e",
        "bg_card": "#16213e",
        "text_primary": "#ffffff",
        "text_secondary": "#e0e0e0",
        "text_muted": "#888888",
    },
    "ocean_tech": {
        "name": "海洋科技",
        "primary_gradient": "linear-gradient(135deg, #0093E9 0%, #80D0C7 100%)",
        "secondary_gradient": "linear-gradient(135deg, #00c6fb 0%, #005bea 100%)",
        "accent_gradient": "linear-gradient(135deg, #c471f5 0%, #fa71cd 100%)",
        "warm_gradient": "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
        "colors": {
            "blockchain": "#0093E9",
            "defi": "#c471f5",
            "nft": "#00c6fb",
            "regulation": "#fa71cd",
            "market": "#80D0C7",
            "feature": "#005bea",
        },
        "bg_primary": "#f0f9ff",
        "bg_card": "#ffffff",
        "text_primary": "#1e3a5f",
        "text_secondary": "#4a6fa5",
        "text_muted": "#94a3b8",
    }
}

# 默认主题
DEFAULT_THEME = "cyberpunk"

# ============================================================
# 分类配置
# ============================================================

CATEGORIES = {
    "blockchain": {"icon": "⛓️", "name": "区块链技术", "name_en": "Blockchain"},
    "defi": {"icon": "💰", "name": "DeFi动态", "name_en": "DeFi"},
    "nft": {"icon": "🎨", "name": "NFT市场", "name_en": "NFT"},
    "regulation": {"icon": "⚖️", "name": "监管政策", "name_en": "Regulation"},
    "market": {"icon": "📈", "name": "市场行情", "name_en": "Market"},
}

# ============================================================
# 基础样式
# ============================================================

BASE_STYLES = """
font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
"""

# ============================================================
# 组件模板函数
# ============================================================

def get_theme(theme_name=None):
    """获取主题配置"""
    return THEMES.get(theme_name or DEFAULT_THEME, THEMES[DEFAULT_THEME])


def render_date_card(weekday, date_str, lunar_str, theme=None):
    """渲染日期卡片"""
    t = get_theme(theme)
    return f'''<section style="text-align: center; padding: 22px 18px; background: {t['primary_gradient']}; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
<p style="margin: 0; font-size: 13px; color: rgba(255,255,255,0.85); letter-spacing: 1px;">⛓️ 每日洞察 · 拥抱未来 ⛓️</p>
<p style="margin: 8px 0; font-size: 26px; font-weight: bold; color: #fff; letter-spacing: 3px; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">{weekday}</p>
<p style="margin: 0; font-size: 13px; color: rgba(255,255,255,0.9);">{date_str} · {lunar_str}</p>
</section>'''


def render_feature_section(title, background, analysis, outlook, theme=None):
    """渲染深度专题区块"""
    t = get_theme(theme)
    feature_color = t['colors']['feature']
    return f'''<section style="margin-bottom: 22px;">
<p style="display: inline-block; background: {t['accent_gradient']}; color: #fff; font-size: 16px; font-weight: bold; padding: 8px 20px; border-radius: 25px; margin: 0 0 14px 0; box-shadow: 0 3px 10px rgba(245, 87, 108, 0.3);">🔥 深度专题</p>
<div style="background: {t['bg_primary']}; padding: 18px; border-radius: 12px; border-left: 4px solid {feature_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
<p style="margin: 0 0 14px 0; font-size: 18px; font-weight: bold; color: {t['text_primary']}; line-height: 1.5;">{title}</p>
<p style="margin: 0 0 10px 0; font-size: 14px; font-weight: bold; color: {feature_color};">📊 事件背景</p>
<p style="margin: 0 0 12px 0; font-size: 14px; line-height: 1.9; color: {t['text_secondary']};">{background}</p>
<p style="margin: 0 0 10px 0; font-size: 14px; font-weight: bold; color: {feature_color};">🔍 深度解析</p>
<p style="margin: 0 0 12px 0; font-size: 14px; line-height: 1.9; color: {t['text_secondary']};">{analysis}</p>
<p style="margin: 0 0 10px 0; font-size: 14px; font-weight: bold; color: {feature_color};">💡 趋势展望</p>
<p style="margin: 0; font-size: 14px; line-height: 1.9; color: {t['text_secondary']};">{outlook}</p>
</div>
</section>'''


def render_news_header(theme=None):
    """渲染今日要闻标题"""
    t = get_theme(theme)
    return f'''<p style="display: inline-block; background: {t['secondary_gradient']}; color: #fff; font-size: 16px; font-weight: bold; padding: 8px 20px; border-radius: 25px; margin: 0 0 14px 0; box-shadow: 0 3px 10px rgba(79, 172, 254, 0.3);">📰 今日要闻</p>'''


def render_category_section(category_key, news_items, theme=None):
    """渲染分类新闻区块"""
    t = get_theme(theme)
    cat = CATEGORIES.get(category_key, {"icon": "📌", "name": category_key})
    color = t['colors'].get(category_key, "#667eea")

    news_html = ""
    for idx, item in enumerate(news_items, 1):
        # 支持两种格式：纯文字 或 {title, detail} 字典
        if isinstance(item, dict):
            title = item.get('title', '')
            detail = item.get('detail', '')
            detail_html = f' <span style="color: {t["text_muted"]}; font-size: 13px;">- {detail}</span>' if detail else ''
        else:
            title = item
            detail_html = ''

        news_html += f'''<p style="margin: 0 0 11px 0; line-height: 1.9; color: {t['text_primary']}; font-size: 14px;"><span style="display: inline-block; background: {color}; color: #fff; font-weight: bold; padding: 2px 8px; border-radius: 4px; margin-right: 8px; font-size: 12px;">{idx:02d}</span>{title}{detail_html}</p>
'''

    return f'''<section style="margin-bottom: 20px;">
<p style="display: inline-block; color: {color}; font-size: 16px; font-weight: bold; padding: 8px 0; margin: 0 0 12px 0; border-bottom: 2px solid {color};">{cat['icon']} {cat['name']}</p>
<div style="padding: 0 10px;">
{news_html.rstrip()}
</div>
</section>'''


def render_footer(slogan="用智慧拥抱Web3未来", subtitle="即使市场波动，技术进步的脚步从未停止", theme=None):
    """渲染尾标区块"""
    t = get_theme(theme)
    return f'''<section style="padding: 20px; background: {t['warm_gradient']}; border-radius: 12px; text-align: center; margin-top: 22px; box-shadow: 0 2px 10px rgba(0,0,0,0.08);">
<p style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: {t['text_primary']};">💡 {slogan}</p>
<p style="margin: 0; font-size: 13px; color: {t['text_secondary']}; line-height: 1.6;">{subtitle}</p>
<p style="margin: 8px 0 0 0; font-size: 12px; color: {t['text_muted']};">—— 三更Web3，每日陪伴</p>
</section>'''


def render_qrcode_section(qrcode_url, theme=None):
    """渲染二维码区块"""
    t = get_theme(theme)
    return f'''<section style="text-align: center; margin-top: 22px; padding: 18px;">
<p style="margin: 0 0 10px 0; font-size: 16px; font-weight: 600; color: {t['text_primary']};">👥 加入三更Web3社区</p>
<p style="margin: 0 0 14px 0; font-size: 13px; color: {t['text_secondary']}; line-height: 1.5;">与5000+Web3爱好者一起<br>探讨行业前沿，分享投资心得</p>
<img src="{qrcode_url}" style="width: 160px; height: 160px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.12);">
<p style="margin: 12px 0 0 0; font-size: 12px; color: {t['text_muted']};">长按识别，关注三更Web3</p>
</section>'''


def render_brand_banner(banner_url=None, theme=None):
    """渲染品牌标题栏（如果有图片素材）"""
    if not banner_url:
        return ""
    return f'''<img src="{banner_url}" style="width: 100%; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">'''


def render_divider(theme=None):
    """渲染分割线"""
    t = get_theme(theme)
    return f'''<div style="height: 1px; background: linear-gradient(90deg, transparent, {t['colors']['blockchain']}40, transparent); margin: 20px 0;"></div>'''


# ============================================================
# 完整页面渲染
# ============================================================

def render_full_page(data, theme=None):
    """
    渲染完整的 Web3 日报页面

    Args:
        data: dict 包含以下字段:
            - weekday: str 星期几
            - date_str: str 日期字符串
            - lunar_str: str 农历字符串
            - feature: dict 深度专题 {title, background, analysis, outlook}
            - news: dict 分类新闻 {blockchain: [], defi: [], nft: [], regulation: [], market: []}
            - qrcode_url: str 二维码URL
            - banner_url: str (可选) 标题栏图片URL
            - slogan: str (可选) 尾标标语
        theme: str 主题名称

    Returns:
        str: 完整的 HTML 内容
    """
    t = get_theme(theme)

    # 构建各部分
    html_parts = []

    # 容器开始
    html_parts.append(f'<section style="padding: 15px; {BASE_STYLES}">')

    # 品牌标题栏（可选）
    if data.get('banner_url'):
        html_parts.append(render_brand_banner(data['banner_url'], theme))

    # 日期卡片
    html_parts.append(render_date_card(
        data['weekday'],
        data['date_str'],
        data['lunar_str'],
        theme
    ))

    # 深度专题
    if data.get('feature'):
        f = data['feature']
        html_parts.append(render_feature_section(
            f.get('title', ''),
            f.get('background', ''),
            f.get('analysis', ''),
            f.get('outlook', ''),
            theme
        ))

    # 今日要闻标题
    html_parts.append(render_news_header(theme))

    # 各分类新闻
    news = data.get('news', {})
    category_order = ['blockchain', 'defi', 'nft', 'regulation', 'market']
    for cat_key in category_order:
        if cat_key in news and news[cat_key]:
            html_parts.append(render_category_section(cat_key, news[cat_key], theme))

    # 尾标
    slogan = data.get('slogan', '用智慧拥抱Web3未来')
    subtitle = data.get('subtitle', '即使市场波动，技术进步的脚步从未停止')
    html_parts.append(render_footer(slogan, subtitle, theme))

    # 二维码
    if data.get('qrcode_url'):
        html_parts.append(render_qrcode_section(data['qrcode_url'], theme))

    # 容器结束
    html_parts.append('</section>')

    return '\n\n'.join(html_parts)


# ============================================================
# 测试 / 预览
# ============================================================

def preview_theme(theme_name=None):
    """生成主题预览的测试数据"""
    test_data = {
        "weekday": "星期五",
        "date_str": "2026年01月31日",
        "lunar_str": "乙巳年腊月十三",
        "feature": {
            "title": "比特币突破10万美元：机构入场与减半效应双重推动",
            "background": "2026年1月30日，比特币价格突破10万美元大关，创下历史新高。这一里程碑式的突破标志着加密货币市场进入新阶段。",
            "analysis": "本轮上涨主要受三大因素推动：1）美国多只比特币现货ETF获批后，机构资金持续流入；2）2024年减半效应逐步显现；3）全球宏观环境转向宽松，美联储降息预期升温。",
            "outlook": "短期来看，10万美元关口可能面临获利回吐压力；中期来看，机构配置需求仍在增长，支撑价格维持高位运行。"
        },
        "news": {
            "blockchain": [
                {"title": "以太坊Pectra升级测试网上线", "detail": "预计Q2主网部署"},
                {"title": "Solana日活跃地址突破500万", "detail": "创历史新高"},
                {"title": "Base网络TVL突破100亿美元", "detail": "成为第二大L2"}
            ],
            "defi": [
                {"title": "Aave v4正式上线以太坊主网", "detail": "资本效率提升40%"},
                {"title": "Uniswap v4部署完成", "detail": "引入Hooks机制"},
                {"title": "DeFi总TVL突破2000亿美元", "detail": "创两年新高"}
            ],
            "nft": [
                {"title": "Pudgy Penguins地板价突破30ETH", "detail": "周涨幅超50%"},
                {"title": "OpenSea推出零手续费交易", "detail": "应对Blur竞争"},
                {"title": "比特币NFT市值突破20亿美元", "detail": "Ordinals生态繁荣"}
            ],
            "regulation": [
                {"title": "美国国会通过《加密市场结构法案》", "detail": "明确SEC/CFTC管辖权"},
                {"title": "欧盟MiCA法规正式生效", "detail": "统一监管框架"},
                {"title": "香港批准第二批虚拟资产交易所牌照", "detail": "5家机构获批"}
            ],
            "market": [
                {"title": "比特币突破10万美元", "detail": "市值超2万亿美元"},
                {"title": "加密市场总市值达3.5万亿美元", "detail": "创历史新高"},
                {"title": "比特币ETF单周净流入50亿美元", "detail": "机构持续加仓"}
            ]
        },
        "qrcode_url": "https://cdn.jsdelivr.net/gh/lairulan/png@main/web3-daily/wechat-qrcode.png"
    }
    return test_data


if __name__ == "__main__":
    import sys

    # 支持命令行测试
    theme = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_THEME

    print(f"=== Web3日报 HTML 模板系统 ===")
    print(f"当前主题: {theme}")
    print(f"可用主题: {', '.join(THEMES.keys())}")
    print()

    # 生成预览
    test_data = preview_theme(theme)
    html = render_full_page(test_data, theme)

    # 保存预览文件
    import os
    preview_path = os.path.expanduser(f"~/Downloads/web3_template_preview_{theme}.html")

    full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Web3日报模板预览 - {theme}</title>
<style>
body {{ max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
</style>
</head>
<body>
{html}
</body>
</html>'''

    with open(preview_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"✅ 预览文件已保存: {preview_path}")
    print(f"   使用浏览器打开查看效果")
