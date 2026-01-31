#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片上传到图床工具
支持上传本地图片到 ImgBB，返回可用URL
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 创建 SSL 上下文
ssl_context = ssl._create_unverified_context()

# ImgBB API配置（免费，无需注册）
IMGBB_API_KEY = "d139e0e38dbe89f50b5dd73b6f9c7e70"  # 公共测试Key
IMGBB_API_URL = "https://api.imgbb.com/1/upload"

def upload_image_to_imgbb(image_path, name=None):
    """
    上传图片到ImgBB图床

    Args:
        image_path: 图片文件路径
        name: 图片名称（可选）

    Returns:
        dict: 包含上传结果的字典
    """
    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": f"文件不存在: {image_path}"
        }

    try:
        # 读取图片并转为base64
        with open(image_path, 'rb') as f:
            image_data = f.read()

        base64_image = base64.b64encode(image_data).decode('utf-8')

        # 准备请求数据
        data = {
            'key': IMGBB_API_KEY,
            'image': base64_image
        }

        if name:
            data['name'] = name

        # 编码数据
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')

        # 发送请求
        req = urllib.request.Request(IMGBB_API_URL, data=encoded_data)

        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
            result = json.loads(response.read().decode('utf-8'))

        if result.get('success'):
            return {
                "success": True,
                "url": result['data']['url'],
                "display_url": result['data']['display_url'],
                "delete_url": result['data'].get('delete_url')
            }
        else:
            return {
                "success": False,
                "error": result.get('error', {}).get('message', 'Unknown error')
            }

    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"网络错误: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"上传失败: {str(e)}"
        }

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 upload_image.py <图片路径> [图片名称]")
        print("\n示例:")
        print("  python3 upload_image.py ~/path/to/image.png")
        print("  python3 upload_image.py ~/path/to/image.png my-image")
        sys.exit(1)

    image_path = os.path.expanduser(sys.argv[1])
    name = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"📤 正在上传图片: {image_path}")

    result = upload_image_to_imgbb(image_path, name)

    if result['success']:
        print(f"\n✅ 上传成功！")
        print(f"📸 图片URL: {result['url']}")
        print(f"🔗 展示URL: {result['display_url']}")
        if result.get('delete_url'):
            print(f"🗑️  删除URL: {result['delete_url']}")

        # 输出JSON格式（方便脚本调用）
        print(f"\nJSON: {json.dumps(result, ensure_ascii=False)}")
    else:
        print(f"\n❌ 上传失败: {result['error']}")
        sys.exit(1)

if __name__ == '__main__':
    main()
