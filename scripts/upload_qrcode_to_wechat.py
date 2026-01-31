#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传二维码到微信公众号素材库

使用微绿流量宝API获取access_token，然后直接调用微信API上传图片到永久素材库
"""

import os
import sys
import requests
import json

# API配置
API_BASE = "https://wx.limyai.com/api/openapi"
WECHAT_API_KEY = os.environ.get("WEB3_WECHAT_API_KEY", "")
WECHAT_APP_ID = os.environ.get("WEB3_WECHAT_APPID", "wx8a65cfea3de65092")

# 二维码路径
QRCODE_PATH = os.path.expanduser("~/.claude/skills/web3-daily/web3-daily/assets/brand-materials/qrcode/wechat-qrcode.png")

def get_wechat_access_token():
    """
    通过微绿流量宝API获取微信access_token
    """
    print("🔑 获取微信access_token...")

    url = f"{API_BASE}/wechat-token"
    headers = {
        "X-API-Key": WECHAT_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "wechatAppid": WECHAT_APP_ID
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()

        if result.get('success'):
            access_token = result['data']['access_token']
            expires_in = result['data'].get('expires_in', 7200)
            print(f"✅ Access Token获取成功 (有效期: {expires_in}秒)")
            print(f"   Token: {access_token[:20]}...")
            print()
            return access_token
        else:
            print(f"❌ 获取失败: {result}")
            return None

    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def upload_image_to_wechat_material(access_token, image_path):
    """
    上传图片到微信公众号永久素材库

    微信API文档: https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/New_temporary_materials.html
    """
    print("📤 上传图片到微信永久素材库...")
    print(f"   文件: {image_path}")
    print(f"   大小: {os.path.getsize(image_path) / 1024:.2f} KB")
    print()

    # 微信API: 新增永久素材
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"

    try:
        with open(image_path, 'rb') as f:
            files = {
                'media': ('wechat-qrcode.png', f, 'image/png')
            }
            # 注意: 永久素材需要额外的type参数
            data = {
                'type': 'image'
            }

            response = requests.post(url, files=files, data=data, timeout=60)

        result = response.json()

        print(f"API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        print()

        if 'media_id' in result:
            print("=" * 60)
            print("✅ 上传成功！")
            print("=" * 60)
            print()
            print(f"📋 Media ID: {result['media_id']}")
            print(f"🔗 图片URL: {result['url']}")
            print()
            print("💡 使用方法:")
            print("   在HTML中直接使用此URL:")
            print(f"   <img src=\"{result['url']}\" />")
            print()
            return {
                'success': True,
                'media_id': result['media_id'],
                'url': result['url']
            }
        elif 'errcode' in result:
            # 错误处理
            errcode = result['errcode']
            errmsg = result.get('errmsg', 'Unknown error')

            print("=" * 60)
            print("❌ 上传失败")
            print("=" * 60)
            print()
            print(f"错误码: {errcode}")
            print(f"错误信息: {errmsg}")
            print()

            # 常见错误码说明
            error_messages = {
                40001: "access_token无效或已过期",
                40003: "无效的openid",
                40004: "无效的媒体类型",
                40007: "无效的media_id",
                41001: "缺少access_token参数",
                41002: "缺少appid参数",
                41003: "缺少refresh_token参数",
                41004: "缺少secret参数",
                41005: "缺少媒体文件数据",
                41006: "缺少media_id参数",
                42001: "access_token超时",
                43001: "需要GET请求",
                43002: "需要POST请求",
                43003: "需要HTTPS请求",
                43004: "需要接收者关注",
                43005: "需要好友关系",
                44001: "空白的媒体文件",
                44002: "POST包为空",
                44003: "图文消息内容为空",
                44004: "文本消息内容为空",
                45001: "媒体文件过大",
                45002: "消息内容过长",
                45003: "标题字段过长",
                45004: "描述字段过长",
                45005: "链接字段过长",
                45006: "图片链接字段过长",
                45007: "语音播放时间超过限制",
                45008: "图文消息超过限制",
                45009: "接口调用超过限制",
                47001: "JSON/XML内容解析失败",
                48001: "api功能未授权"
            }

            if errcode in error_messages:
                print(f"说明: {error_messages[errcode]}")
                print()

            return {'success': False, 'errcode': errcode, 'errmsg': errmsg}
        else:
            print("❌ 未知响应格式")
            return {'success': False}

    except Exception as e:
        print(f"❌ 上传异常: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def upload_image_to_wechat_temp(access_token, image_path):
    """
    上传图片到微信公众号临时素材库 (有效期3天)

    如果永久素材上传失败，可以尝试临时素材
    """
    print("📤 尝试上传到临时素材库 (有效期3天)...")

    url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=image"

    try:
        with open(image_path, 'rb') as f:
            files = {
                'media': ('wechat-qrcode.png', f, 'image/png')
            }
            response = requests.post(url, files=files, timeout=60)

        result = response.json()

        if 'media_id' in result:
            print("✅ 临时素材上传成功")
            print(f"Media ID: {result['media_id']}")
            print(f"有效期: 3天")
            print()
            return {'success': True, 'media_id': result['media_id'], 'type': 'temp'}
        else:
            print(f"❌ 失败: {result}")
            return {'success': False}

    except Exception as e:
        print(f"❌ 异常: {e}")
        return {'success': False}

def main():
    print("=" * 60)
    print("微信公众号二维码自动上传工具")
    print("=" * 60)
    print()
    print(f"公众号: 三更Web3 (Neo-法恒)")
    print(f"AppID: {WECHAT_APP_ID}")
    print(f"二维码: {QRCODE_PATH}")
    print()

    # 检查文件是否存在
    if not os.path.exists(QRCODE_PATH):
        print(f"❌ 错误: 二维码文件不存在")
        print(f"   路径: {QRCODE_PATH}")
        return None

    # 1. 获取access_token
    access_token = get_wechat_access_token()
    if not access_token:
        print("❌ 无法获取access_token，终止上传")
        return None

    # 2. 上传到永久素材库
    result = upload_image_to_wechat_material(access_token, QRCODE_PATH)

    if result.get('success'):
        print("=" * 60)
        print("🎉 成功！")
        print("=" * 60)
        print()
        print("下一步:")
        print("1. 复制上面的图片URL")
        print("2. 在HTML模板中替换占位符:")
        print("   将 'https://i.ibb.co/placeholder/wechat-qrcode.png'")
        print(f"   替换为 '{result['url']}'")
        print("3. 重新生成并发布文章")
        print()
        return result
    else:
        # 永久素材失败，尝试临时素材
        print()
        print("永久素材上传失败，尝试临时素材...")
        print()
        temp_result = upload_image_to_wechat_temp(access_token, QRCODE_PATH)

        if temp_result.get('success'):
            print()
            print("⚠️  注意: 临时素材只有3天有效期")
            print("   建议改用永久素材或第三方图床")
            return temp_result
        else:
            print()
            print("=" * 60)
            print("❌ 所有上传方式均失败")
            print("=" * 60)
            print()
            print("建议:")
            print("1. 检查access_token是否有效")
            print("2. 确认公众号已认证(永久素材需要认证)")
            print("3. 检查图片格式和大小(需<2MB)")
            print("4. 使用GitHub图床方案替代")
            print()
            return None

if __name__ == "__main__":
    result = main()

    if result:
        # 保存结果到文件
        result_file = os.path.expanduser("~/Downloads/wechat_qrcode_upload_result.json")
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"📄 结果已保存到: {result_file}")
