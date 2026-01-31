#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发布Web3日报到微信公众号草稿箱
"""

import os
import sys
import json
import requests
import re

# API配置
API_BASE = "https://wx.limyai.com/api/openapi"
WECHAT_API_KEY = os.environ.get("WEB3_WECHAT_API_KEY", "")
WECHAT_APP_ID = os.environ.get("WEB3_WECHAT_APPID", "wx8a65cfea3de65092")

# 读取生成的HTML内容 - 使用移动端优化版本v2(紧凑版)
html_file = os.path.expanduser("~/Documents/Obsidian/Web3日报/2026-01-30_Web3日报_移动端_v2.html")

print("📤 准备发布Web3日报到微信公众号...")
print(f"公众号: 三更Web3 (Neo-法恒)")
print(f"AppID: {WECHAT_APP_ID}")
print(f"文件: {html_file}")
print()

# 读取HTML内容
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# 提取body内容（去掉DOCTYPE和html标签）
body_match = re.search(r'<body[^>]*>(.*)</body>', html_content, re.DOTALL)
if body_match:
    content = body_match.group(1)
else:
    content = html_content

print(f"✅ HTML内容已加载 ({len(content)} 字符)")

# 准备发布数据 - 更新日期为1月30日
title = "1月30日Web3日报：比特币暴跌至85,000美元，技术支撑崩溃引发市场恐慌"
summary = "比特币跌破100周均线至85,200美元，ETF五日净流出11亿美元；Layer2 TVL达470亿美元，NFT市场回暖；美国参议院推进CLARITY法案"

data = {
    "wechatAppid": WECHAT_APP_ID,
    "title": title,
    "content": content,
    "digest": summary,
    "contentFormat": "html",
    "type": "news"
}

print(f"📝 标题: {title}")
print(f"📋 摘要: {summary}")
print()

# 发送请求
print("🚀 正在发布到草稿箱...")

url = f"{API_BASE}/wechat-publish"
headers = {
    "X-API-Key": WECHAT_API_KEY,
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=30)

    print(f"HTTP状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print()
        print("=" * 60)
        print("✅ 发布成功！")
        print("=" * 60)
        print()
        print(f"📱 公众号: 三更Web3 (Neo-法恒)")
        print(f"📄 文章标题: {title}")
        print(f"📊 内容大小: {len(content)} 字符")
        print()
        print("💡 下一步:")
        print("1. 登录微信公众平台: https://mp.weixin.qq.com")
        print("2. 进入'素材管理' → '草稿'")
        print("3. 找到刚才发布的文章")
        print("4. 在底部二维码区域添加真实的个人微信二维码")
        print("5. 预览确认移动端显示效果")
        print("6. 确认无误后发布")
        print()

        if result:
            print("API返回:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print()
        print("❌ 发布失败")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")

except requests.exceptions.Timeout:
    print()
    print("❌ 请求超时，请检查网络连接")

except requests.exceptions.RequestException as e:
    print()
    print(f"❌ 请求异常: {e}")

except Exception as e:
    print()
    print(f"❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()
