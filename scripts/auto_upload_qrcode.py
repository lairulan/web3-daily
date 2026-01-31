#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二维码自动上传解决方案

提供多种方案自动上传二维码到图床，解决微信公众号发布时二维码显示问题
"""

import os
import sys
import base64
import requests
import json

# 二维码本地路径
QRCODE_PATH = os.path.expanduser("~/.claude/skills/web3-daily/web3-daily/assets/brand-materials/qrcode/wechat-qrcode.png")

print("=" * 60)
print("二维码自动上传解决方案")
print("=" * 60)
print()

# ============================================================================
# 方案1: SM.MS 图��� (推荐 - 免费稳定)
# ============================================================================
def upload_to_smms():
    """
    使用 SM.MS 图床上传
    - 免费: 5MB/文件, 10GB总空间
    - 无需API Key (游客模式)
    - 有API Key更稳定
    """
    print("📤 方案1: SM.MS 图床上传")
    print("-" * 60)

    url = "https://sm.ms/api/v2/upload"

    # 如果有API Key，可以提供更稳定的服务
    # 注册地址: https://sm.ms/home/apitoken
    headers = {
        # 'Authorization': 'your-api-token-here'  # 可选
    }

    try:
        with open(QRCODE_PATH, 'rb') as f:
            files = {'smfile': f}
            response = requests.post(url, files=files, headers=headers, timeout=30)

        result = response.json()

        if result.get('success'):
            image_url = result['data']['url']
            print(f"✅ 上传成功！")
            print(f"图片URL: {image_url}")
            print()
            return image_url
        else:
            print(f"❌ 上传失败: {result.get('message')}")
            if result.get('code') == 'image_repeated':
                # 图片已存在，返回已有URL
                image_url = result['images']
                print(f"✅ 图片已存在，使用现有URL")
                print(f"图片URL: {image_url}")
                print()
                return image_url
            print()
            return None

    except Exception as e:
        print(f"❌ 异常: {e}")
        print()
        return None

# ============================================================================
# 方案2: 路过图床 (国内稳定)
# ============================================================================
def upload_to_imgtu():
    """
    使用路过图床 (imgtu.com)
    - 国内访问快
    - 免费10MB/文件
    - 支持API
    """
    print("📤 方案2: 路过图床上传")
    print("-" * 60)

    url = "https://imgtu.com/api/1/upload"

    try:
        with open(QRCODE_PATH, 'rb') as f:
            files = {
                'source': f,
                'key': '6d207e02198a847aa98d0a2a901485a5',  # 公共API Key
            }
            response = requests.post(url, files=files, timeout=30)

        result = response.json()

        if result.get('status_code') == 200:
            image_url = result['image']['url']
            print(f"✅ 上传成功！")
            print(f"图片URL: {image_url}")
            print()
            return image_url
        else:
            print(f"❌ 上传失败: {result.get('error', {}).get('message')}")
            print()
            return None

    except Exception as e:
        print(f"❌ 异常: {e}")
        print()
        return None

# ============================================================================
# 方案3: GitHub 作为图床 (永久稳定)
# ============================================================================
def upload_to_github():
    """
    使用 GitHub 仓库作为图床
    - 完全免费
    - 永久稳定
    - 需要创建 GitHub Token

    步骤:
    1. 创建GitHub仓库 (如: username/image-hosting)
    2. 生成Token: Settings → Developer settings → Personal access tokens → Generate new token
    3. 权限选择: repo (所有)
    4. 将Token填入下方
    """
    print("📤 方案3: GitHub 图床上传")
    print("-" * 60)

    # 配置
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
    GITHUB_REPO = "lairulan/png"  # 格式: username/repo
    GITHUB_PATH = "web3-daily/wechat-qrcode.png"  # 文件在仓库中的路径

    if not GITHUB_TOKEN:
        print("⚠️  需要配置 GITHUB_TOKEN 环境变量")
        print("   获取方法: https://github.com/settings/tokens")
        print()
        return None

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}"

    try:
        # 读取文件并base64编码
        with open(QRCODE_PATH, 'rb') as f:
            content = base64.b64encode(f.read()).decode()

        # 准备数据
        data = {
            "message": "Upload WeChat QR code",
            "content": content,
        }

        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        # 先检查文件是否存在
        check_response = requests.get(url, headers=headers)
        if check_response.status_code == 200:
            # 文件存在，需要更新
            data["sha"] = check_response.json()["sha"]

        # 上传或更新文件
        response = requests.put(url, headers=headers, json=data, timeout=30)

        if response.status_code in [200, 201]:
            result = response.json()
            # GitHub raw URL
            raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_PATH}"
            # 或使用 jsdelivr CDN 加速
            cdn_url = f"https://cdn.jsdelivr.net/gh/{GITHUB_REPO}@main/{GITHUB_PATH}"

            print(f"✅ 上传成功！")
            print(f"GitHub URL: {result['content']['html_url']}")
            print(f"Raw URL: {raw_url}")
            print(f"CDN URL (加速): {cdn_url}")
            print()
            return cdn_url
        else:
            print(f"❌ 上传失败: {response.status_code}")
            print(f"响应: {response.text}")
            print()
            return None

    except Exception as e:
        print(f"❌ 异常: {e}")
        print()
        return None

# ============================================================================
# 方案4: Base64 嵌入 (不推荐但最简单)
# ============================================================================
def convert_to_base64():
    """
    将图片转为base64嵌入HTML
    - 优点: 无需上传，直接使用
    - 缺点: 增加HTML大小，可能被微信过滤
    """
    print("📤 方案4: Base64 嵌入")
    print("-" * 60)

    try:
        with open(QRCODE_PATH, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode()

        # 构建data URI
        data_uri = f"data:image/png;base64,{base64_data}"

        print(f"✅ 转换成功！")
        print(f"Base64大小: {len(base64_data)} 字符")
        print(f"Data URI (前100字符): {data_uri[:100]}...")
        print()
        print("⚠️  注意: 微信公众号可能不支持base64图片")
        print()

        return data_uri

    except Exception as e:
        print(f"❌ 异常: {e}")
        print()
        return None

# ============================================================================
# 主函数 - 尝试所有方案
# ============================================================================
def main():
    print(f"本地二维码: {QRCODE_PATH}")
    print(f"文件存在: {os.path.exists(QRCODE_PATH)}")
    print()

    if not os.path.exists(QRCODE_PATH):
        print("❌ 二维码文件不存在！")
        return None

    print("开始尝试上传...")
    print()

    # 按优先级尝试各个方案

    # 方案1: SM.MS (推荐)
    url = upload_to_smms()
    if url:
        print("=" * 60)
        print("✅ 成功！使用此URL更新HTML:")
        print(f"   {url}")
        print("=" * 60)
        return url

    # 方案2: 路过图床
    url = upload_to_imgtu()
    if url:
        print("=" * 60)
        print("✅ 成功！使用此URL更新HTML:")
        print(f"   {url}")
        print("=" * 60)
        return url

    # 方案3: GitHub (需要配置)
    url = upload_to_github()
    if url:
        print("=" * 60)
        print("✅ 成功！使用此URL更新HTML:")
        print(f"   {url}")
        print("=" * 60)
        return url

    # 方案4: Base64 (最后备选)
    print("所有图床上传失败，尝试Base64方案...")
    print()
    data_uri = convert_to_base64()
    if data_uri:
        print("=" * 60)
        print("⚠️  使用Base64方案 (可能被微信过滤)")
        print("=" * 60)
        return data_uri

    print("=" * 60)
    print("❌ 所有方案均失败")
    print("=" * 60)
    print()
    print("建议:")
    print("1. 检查网络连接")
    print("2. 配置GitHub Token使用方案3")
    print("3. 在微信公众号后台手动上传二维码")
    print()

    return None

# ============================================================================
# 推荐配置方案
# ============================================================================
def print_recommendations():
    print()
    print("=" * 60)
    print("📋 推荐配置方案")
    print("=" * 60)
    print()

    print("方案A: SM.MS (最简单)")
    print("-" * 60)
    print("1. 访问: https://sm.ms/home/apitoken")
    print("2. 注册账号并生成API Token")
    print("3. 在脚本中配置Token")
    print("4. 每次运行自动上传")
    print()

    print("方案B: GitHub图床 (最稳定)")
    print("-" * 60)
    print("1. 创建GitHub仓库: https://github.com/new")
    print("   仓库名如: image-hosting, 设为Public")
    print("2. 生成Token: https://github.com/settings/tokens")
    print("   权限选择: repo (全部)")
    print("3. 配置环境变量:")
    print("   export GITHUB_TOKEN='your_token_here'")
    print("4. 修改脚本中的 GITHUB_REPO 为你的仓库")
    print("5. 每次运行自动上传到GitHub")
    print()

    print("方案C: 自动化脚本整合")
    print("-" * 60)
    print("将此上传脚本整合到 auto_web3_daily.py 中:")
    print("1. 生成HTML前先上传二维码")
    print("2. 获取图片URL")
    print("3. 在HTML中使用真实URL")
    print("4. 完全自动化，无需手动操作")
    print()

if __name__ == "__main__":
    result_url = main()
    print_recommendations()

    if result_url:
        print()
        print("✅ 下一步: 将URL复制到HTML模板中")
        print(f"   替换: https://i.ibb.co/placeholder/wechat-qrcode.png")
        print(f"   为: {result_url}")
