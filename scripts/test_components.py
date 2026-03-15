#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web3日报测试脚本 - 验证所有组件
"""

import os
import sys
from datetime import datetime, timedelta

# 设置路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

print("🧪 Web3日报组件测试")
print("=" * 60)

# 测试1: 检查二维码文件
print("\n1️⃣ 测试二维码文件...")
qrcode_path = os.path.join(SKILL_DIR, 'assets/brand-materials/qrcode/wechat-qrcode.png')
if os.path.exists(qrcode_path):
    size = os.path.getsize(qrcode_path) / 1024
    print(f"   ✅ 二维码文件存在: {size:.1f} KB")
else:
    print(f"   ❌ 二维码文件不存在")

# 测试2: 检查环境变量
print("\n2️⃣ 测试环境变量...")
env_vars = {
    'DOUBAO_API_KEY': os.environ.get('DOUBAO_API_KEY'),
}

for key, value in env_vars.items():
    if value:
        print(f"   ✅ {key}: 已设置 ({value[:20]}...)")
    else:
        print(f"   ⚠️  {key}: 未设置")

# 测试3: 生成测试HTML
print("\n3️⃣ 测试HTML生成...")

# 模拟新闻数据
test_news = [
    {
        'category': 'DeFi',
        'title': '以太坊Layer2 TVL突破500亿美元',
        'summary': 'Arbitrum和Optimism领跑，生态持续扩张',
        'source': 'The Block'
    },
    {
        'category': '区块链技术',
        'title': '比特币闪电网络容量创历史新高',
        'summary': '达到5500 BTC，支付体验显著改善',
        'source': 'CoinDesk'
    },
    {
        'category': 'NFT',
        'title': 'Blur推出第三季空投计划',
        'summary': '奖励活跃交易者，新增流动性挖矿机制',
        'source': 'Decrypt'
    },
]

# 模拟深度专题
test_article = """## 以太坊Layer2生态大爆发：TVL突破500亿美元的背后

### 📊 事件背景

2026年1月，以太坊Layer2解决方案的总锁仓价值(TVL)首次突破500亿美元大关，相比去年同期增长200%。这一里程碑标志着Layer2技术从"实验阶段"正式进入"主流采用阶段"。

其中，Arbitrum以210亿美元TVL领跑，Optimism紧随其后达到180亿美元，Base、zkSync、StarkNet等新兴Layer2也展现出强劲增长势头。

### 🔍 深度解析

**技术成熟度提升**：Optimistic Rollup和ZK-Rollup技术经过两年优化，交易确认时间从数小时缩短至数分钟，Gas费用降低95%以上，用户体验接近中心化交易所。

**生态协同效应**：DeFi协议（Uniswap、Aave、Curve）率先迁移，带动NFT市场、GameFi项目跟进。跨链桥技术成熟化解了流动性割裂问题，形成"以太坊主网+多Layer2"的立体生态。

**机构资本入场**：Coinbase推出Base链、Sony进军zkEVM，传统机构对Layer2的认可推动了TVL激增。机构级基础设施（托管、合规工具）逐步完善。

### 💡 趋势展望

短期内，Layer2竞争将聚焦于三个方向：1）更低的交易成本（目标<$0.01）；2）更快的最终确认（<1分钟）；3）更好的互操作性（原生跨链）。

长期来看，以太坊"模块化区块链"愿景正在实现：主网负责安全和共识，Layer2处理执行和扩容，数据可用性层提供存储。这种分工将支撑下一个十亿用户进入Web3。

对投资者而言，关注Layer2原生项目（DEX、借贷、衍生品）和基础设施（跨链桥、预言机、钱包）的机会。对开发者而言，Layer2已成为构建DApp的首选平台。
"""

# 导入格式化函数
sys.path.insert(0, SCRIPT_DIR)
try:
    from auto_web3_daily import format_news_html

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    html = format_news_html(test_news, test_article, yesterday)

    # 保存测试HTML
    test_file = os.path.join(SKILL_DIR, '..', '..', '..', 'Documents', 'Obsidian', 'Web3日报', 'test-output.html')
    os.makedirs(os.path.dirname(test_file), exist_ok=True)

    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"   ✅ HTML生成成功")
    print(f"   📄 测试文件: {test_file}")
    print(f"   📏 HTML大小: {len(html)} 字符")

    # 检查二维码是否在HTML中
    if 'wechat-qrcode' in html or 'Neo-法恒' in html or 'ibb.co' in html:
        print(f"   ✅ HTML包含二维码")
    elif '请将二维码保存到' in html:
        print(f"   ⚠️  HTML使用占位符（二维码上传失败）")
    else:
        print(f"   ℹ️  检查二维码状态...")

except Exception as e:
    print(f"   ❌ HTML生成失败: {e}")
    import traceback
    traceback.print_exc()

# 测试4: 检查输出目录
print("\n4️⃣ 测试输出目录...")
obsidian_dir = os.path.expanduser('~/Documents/Obsidian/Web3日报/')
if os.path.exists(obsidian_dir):
    files = os.listdir(obsidian_dir)
    print(f"   ✅ 输出目录存在，包含 {len(files)} 个文件")
else:
    print(f"   ⚠️  输出目录不存在，将在运行时创建")

# 测试总结
print("\n" + "=" * 60)
print("✅ 组件测试完成！")
print("\n📝 下一步：")
print("   在Claude中说: '生成今日Web3日报'")
print("   或运行: python3 auto_web3_daily.py --dry-run")
