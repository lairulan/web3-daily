#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web3日报完整运行脚本
整合RSS采集、内容生成、封面图生成和微信发布的完整流程

使用方法:
    python3 web3_daily_runner.py              # 生成并发布今日Web3日报
    python3 web3_daily_runner.py --dry-run    # 试运行，不发布
    python3 web3_daily_runner.py --date 2026-01-30  # 指定日期
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent

def log(message, level="INFO"):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def check_environment():
    """环境检查"""
    log("开始环境检查...")

    issues = []

    # 检查环境变量
    required_env_vars = {
        'WECHAT_API_KEY': os.environ.get('WECHAT_API_KEY'),
        'WEB3_WECHAT_APPID': os.environ.get('WEB3_WECHAT_APPID'),
    }

    api_keys = {
        'OPENROUTER_API_KEY': os.environ.get('OPENROUTER_API_KEY'),
        'DOUBAO_API_KEY': os.environ.get('DOUBAO_API_KEY'),
    }

    for var_name, value in required_env_vars.items():
        if not value:
            issues.append(f"❌ 环境变量 {var_name} 未设置")
        else:
            log(f"✅ {var_name} 已配置")

    # 至少需要一个 AI API Key
    if not any(api_keys.values()):
        issues.append("❌ 至少需要设置 OPENROUTER_API_KEY 或 DOUBAO_API_KEY")
    else:
        configured = [k for k, v in api_keys.items() if v]
        log(f"✅ AI API 已配置: {', '.join(configured)}")

    # 检查必需脚本
    required_scripts = [
        'rss_web3_collector.py',
        'generate_image.py',
        'publish_to_wechat.py'
    ]

    for script in required_scripts:
        script_path = SCRIPT_DIR / script
        if not script_path.exists():
            issues.append(f"❌ 缺少脚本: {script}")
        else:
            log(f"✅ 脚本存在: {script}")

    # 检查输出目录
    obsidian_dir = Path.home() / "Documents/Obsidian/Web3日报"
    if not obsidian_dir.exists():
        try:
            obsidian_dir.mkdir(parents=True, exist_ok=True)
            log(f"✅ 创建输出目录: {obsidian_dir}")
        except Exception as e:
            issues.append(f"❌ 无法创建输出目录: {e}")
    else:
        log(f"✅ 输出目录存在: {obsidian_dir}")

    if issues:
        log("环境检查失败:", "ERROR")
        for issue in issues:
            print(f"  {issue}")
        return False

    log("✅ 环境检查通过!", "SUCCESS")
    return True

def run_rss_collector(target_date):
    """运行 RSS 新闻采集器"""
    log(f"开始采集 {target_date} 的Web3新闻...")

    collector_script = SCRIPT_DIR / "rss_web3_collector.py"

    try:
        result = subprocess.run(
            [sys.executable, str(collector_script)],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=SCRIPT_DIR
        )

        if result.returncode == 0:
            log("✅ RSS 新闻采集成功")
            print(result.stdout)

            # 查找生成的JSON文件
            today_str = datetime.now().strftime("%Y%m%d")
            json_file = Path.home() / "Downloads" / f"web3_news_{today_str}.json"

            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    news_data = json.load(f)
                total_news = sum(len(v) for v in news_data.values())
                log(f"📊 采集统计: 共 {total_news} 条新闻")
                for category, news_list in news_data.items():
                    log(f"  - {category}: {len(news_list)}条")
                return json_file
            else:
                log(f"⚠️ 未找到采集结果文件: {json_file}", "WARNING")
                return None
        else:
            log(f"❌ RSS 采集失败: {result.stderr}", "ERROR")
            return None

    except subprocess.TimeoutExpired:
        log("❌ RSS 采集超时（>5分钟）", "ERROR")
        return None
    except Exception as e:
        log(f"❌ RSS 采集异常: {e}", "ERROR")
        return None

def generate_cover_image(title, output_path):
    """生成封面图"""
    log("开始生成封面图...")

    image_script = SCRIPT_DIR / "generate_image.py"

    if not image_script.exists():
        log("⚠️ generate_image.py 不存在，跳过封面图生成", "WARNING")
        return None

    try:
        cmd = [
            sys.executable,
            str(image_script),
            'cover',
            '--title', title,
            '--style', 'tech',
            '--size', '2048x2048',
            '--output', str(output_path)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            cwd=SCRIPT_DIR
        )

        if result.returncode == 0:
            log("✅ 封面图生成成功")
            return output_path
        else:
            log(f"⚠️ 封面图生成失败: {result.stderr}", "WARNING")
            return None

    except subprocess.TimeoutExpired:
        log("⚠️ 封面图生成超时", "WARNING")
        return None
    except Exception as e:
        log(f"⚠️ 封面图生成异常: {e}", "WARNING")
        return None

def main():
    parser = argparse.ArgumentParser(description='Web3日报完整运行脚本')
    parser.add_argument('--check-env', action='store_true', help='仅检查环境')
    parser.add_argument('--dry-run', action='store_true', help='试运行，不发布')
    parser.add_argument('--date', type=str, help='指定日期(YYYY-MM-DD)，默认为昨天')
    parser.add_argument('--skip-rss', action='store_true', help='跳过RSS采集（使用已有数据）')

    args = parser.parse_args()

    print("=" * 70)
    print("            Web3 Daily - Web3每日洞察自动发布系统")
    print("=" * 70)
    print()

    # Step 0: 环境检查
    if not check_environment():
        sys.exit(1)

    if args.check_env:
        log("环境检查完成，退出。")
        sys.exit(0)

    print()

    # 确定目标日期
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d')
            target_date_str = args.date
        except ValueError:
            log(f"❌ 日期格式错误: {args.date}，应为 YYYY-MM-DD", "ERROR")
            sys.exit(1)
    else:
        target_date = datetime.now() - timedelta(days=1)
        target_date_str = target_date.strftime('%Y-%m-%d')

    log(f"📅 目标日期: {target_date_str}")
    print()

    # Step 1: RSS 采集
    if not args.skip_rss:
        log("=" * 70)
        log("Step 1: RSS 新闻采集")
        log("=" * 70)

        news_json = run_rss_collector(target_date_str)

        if not news_json:
            log("⚠️ RSS 采集失败，但可以继续使用备用数据", "WARNING")

        print()
    else:
        log("⏭️ 跳过 RSS 采集")
        print()

    # Step 2-4: 内容生成（需要 Claude 环境）
    log("=" * 70)
    log("Step 2-4: 内容生成")
    log("=" * 70)
    log("⚠️ 此步骤需要在 Claude 环境中运行", "WARNING")
    log("请使用以下命令在 Claude 中执行完整流程:")
    log("")
    log("  claude 'Web3日报'  或  claude 'web3-daily'")
    log("")
    log("Claude 将自动完成:")
    log("  - WebSearch 采集补充资讯")
    log("  - AI 分析选择热门话题")
    log("  - 生成深度专题文章(800-1200字)")
    log("  - 格式化为 HTML")
    print()

    # Step 5: 封面图生成
    if not args.dry_run:
        log("=" * 70)
        log("Step 5: 封面图生成")
        log("=" * 70)

        title = f"{target_date.month}月{target_date.day}日Web3日报"
        output_dir = Path.home() / "Documents/Obsidian/Web3日报/images"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{target_date_str}-cover.png"

        cover_image = generate_cover_image(title, output_path)
        print()

    # 完成提示
    log("=" * 70)
    log("✅ Web3日报生成流程完成", "SUCCESS")
    log("=" * 70)
    log("")
    log("📝 下一步:")
    log("1. 在 Claude 中运行完整的内容生成和发布流程")
    log("2. 检查 ~/Documents/Obsidian/Web3日报/ 目录中的输出文件")
    log("3. 验证微信公众号草稿箱中的文章")

    return 0

if __name__ == '__main__':
    sys.exit(main())
