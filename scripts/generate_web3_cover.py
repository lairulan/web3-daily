#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web3日报封面图生成器（优化版）
确保每次都能可靠生成封面图并返回可用的URL
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta

def generate_cover(date_str=None, retry=3):
    """
    生成Web3日报封面图

    Args:
        date_str: 日期字符串，格式：X月X日，如 "1月30日"
        retry: 重试次数

    Returns:
        dict: {
            "success": True/False,
            "url": "图片URL",
            "local_path": "本地路径（如果有）",
            "error": "错误信息（如果失败）"
        }
    """
    # 如果没有提供日期，使用昨天
    if not date_str:
        yesterday = datetime.now() - timedelta(days=1)
        date_str = f"{yesterday.month}月{yesterday.day}日"

    title = f"{date_str}Web3日报"

    print(f"🎨 开始生成封面图: {title}")
    print(f"   风格: tech（科技风）")
    print(f"   尺寸: 2048x2048")
    print(f"   重试次数: {retry}")
    print()

    # 获取脚本路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_script = os.path.join(script_dir, 'generate_image.py')

    if not os.path.exists(image_script):
        return {
            "success": False,
            "error": f"生成脚本不存在: {image_script}"
        }

    # 调用图片生成脚本
    try:
        cmd = [
            sys.executable,
            image_script,
            'cover',
            '--title', title,
            '--style', 'tech',
            '--size', '2048x2048',
            '--retry', str(retry),
            '--retry-delay', '3'
        ]

        print(f"📝 执行命令: {' '.join(cmd)}")
        print()

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5分钟超时
            cwd=script_dir
        )

        if result.returncode == 0:
            # 解析输出，提取JSON结果
            try:
                # 查找最后一行的JSON输出
                output_lines = result.stdout.strip().split('\n')
                for line in reversed(output_lines):
                    line = line.strip()
                    if line.startswith('{') and line.endswith('}'):
                        data = json.loads(line)
                        if data.get('success'):
                            print("✅ 封面图生成成功！")
                            print(f"   URL: {data.get('url', 'N/A')}")
                            print(f"   来源: {data.get('source', 'N/A')}")
                            return {
                                "success": True,
                                "url": data.get('url'),
                                "display_url": data.get('display_url', data.get('url')),
                                "source": data.get('source'),
                                "attempts": data.get('attempts', 1)
                            }

                # 如果没有找到成功的JSON，返回错误
                return {
                    "success": False,
                    "error": "未能从输出中提取图片URL",
                    "output": result.stdout[-500:]  # 最后500字符
                }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"解析输出失败: {e}",
                    "output": result.stdout[-500:]
                }
        else:
            print(f"❌ 封面图生成失败")
            print(f"   返回码: {result.returncode}")
            print(f"   错误输出: {result.stderr[:500]}")
            return {
                "success": False,
                "error": f"生成脚本返回错误码 {result.returncode}",
                "stderr": result.stderr[:500]
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "封面图生成超时（5分钟）"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"封面图生成异常: {str(e)}"
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='生成Web3日报封面图')
    parser.add_argument('--date', type=str, help='日期（如：1月30日）')
    parser.add_argument('--retry', type=int, default=3, help='重试次数')
    parser.add_argument('--test', action='store_true', help='测试模式')

    args = parser.parse_args()

    if args.test:
        print("=" * 70)
        print("封面图生成测试")
        print("=" * 70)
        print()

    result = generate_cover(date_str=args.date, retry=args.retry)

    if args.test:
        print()
        print("=" * 70)
        print("测试结果:")
        print("=" * 70)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    # 输出JSON结果（供其他脚本调用）
    print()
    print(json.dumps(result, ensure_ascii=False))

    return 0 if result.get('success') else 1


if __name__ == '__main__':
    sys.exit(main())
