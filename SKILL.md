---
name: web3-daily
version: 1.0.0
description: Web3每日洞察自动发布助手。每天自动采集中英文Web3资讯（区块链技术、DeFi、NFT、市场行情、监管政策），翻译成中文，生成混合形式内容（10-15条热点要闻+800-1200字深度专题），自动发布到"三更Web3"微信公众号。触发词："Web3日报"、"生成Web3文章"、"Web3每日洞察"、"web3 daily"。
author: rulanlai
tags: [web3, blockchain, defi, nft, wechat, automation]
---

# Web3 Daily - Web3每日洞察

每天自动采集全球Web3资讯，生成混合形式内容并发布到微信公众号"三更Web3"。

## 功能概述

- 🌍 **中英文双语采集** - 覆盖全球权威Web3媒体
- 🔄 **智能翻译** - 英文资讯自动翻译成中文，保留专业术语
- 📰 **混合内容形式** - 热点要闻(10-15条) + 深度专题(800-1200字)
- 🎨 **精美视觉设计** - 渐变卡片设计 + AI生成封面图
- 📋 **质量检查清单** - 发布前自动验证
- 🤖 **双API降级** - OpenRouter + 豆包双保障
- ⏰ **定时发布** - 每天中午12:00自动推送

## 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                    Web3 Daily Workflow                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 0: 环境预检查                                           │
│   • 脚本文件 • 环境变量 • 网络连通性                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: 资讯采集 (WebSearch)                                 │
│   • 中文媒体：律动、PANews、金色财经                          │
│   • 英文媒体：CoinDesk、The Block、Decrypt                   │
│   • 5大类别：技术/DeFi/NFT/监管/行情                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: 智能翻译与筛选                                        │
│   • 英文资讯翻译成中文 • 保留专业术语 • 筛选15-20条要闻       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: 热门话题选择                                         │
│   • 分析热度 • 选择深度专题话题                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: 深度专题生成                                         │
│   • 800-1200字专业分析 • 结构化内容 • 数据支撑               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: HTML格式化                                           │
│   • 渐变卡片设计 • 分类呈现 • 插入品牌素材                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 6: 封面图生成                                           │
│   • AI生成封面图 • 尺寸2048x2048                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 7: 保存到Obsidian                                       │
│   • 保存Markdown版本 • 归档备份                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 8: 发布到微信公众号                                      │
│   • 三更Web3公众号 • 草稿箱                                  │
└─────────────────────────────────────────────────────────────┘
```

## 详细步骤说明

### Step 0: 环境依赖预检查

运行前自动验证所有依赖是否就绪。

**检查项目**：
1. **环境变量检查**：
   - `WECHAT_API_KEY` (固定值: xhs_fff41080b1861be192872e9cd62399a0)
   - `WEB3_WECHAT_APPID` (需配置)

2. **脚本检查**：
   - `scripts/auto_web3_daily.py`
   - `scripts/generate_image.py`

3. **输出目录**：
   - `~/Documents/Obsidian/Web3日报/`

**决策**：如果依赖缺失，立即停止并报告具体错误。

---

### Step 1: 资讯采集

使用 WebSearch 采集前一天的Web3资讯。

**媒体来源详见**: [references/media_sources.md](references/media_sources.md)

#### 中文媒体搜索词

```
"律动BlockBeats Web3 [昨日日期]"
"PANews 区块链 [昨日日期]"
"金色财经 最新快讯 [昨日日期]"
"Odaily Web3 动态 [昨日日期]"
"链闻 ChainNews [昨日日期]"
```

#### 英文媒体搜索词

```
"CoinDesk crypto news [yesterday]"
"The Block Web3 [yesterday]"
"Decrypt blockchain [yesterday]"
"CoinTelegraph DeFi [yesterday]"
"Blockworks latest [yesterday]"
```

#### 分类搜索（5大类别）

**区块链技术**:
```
"以太坊 升级 [昨日]"
"Bitcoin Layer2 [yesterday]"
"零知识证明 ZK 进展"
"跨链协议 最新"
```

**DeFi动态**:
```
"DeFi 协议 [昨日日期]"
"Uniswap Aave Compound news [yesterday]"
"TVL 锁仓量 变化"
"去中心化交易所 DEX"
```

**NFT市场**:
```
"NFT 市场 [昨日日期]"
"OpenSea 交易量 [yesterday]"
"元宇宙 Metaverse 最新"
"GameFi 链游"
```

**监管政策**:
```
"加密货币 监管 [昨日]"
"SEC crypto [yesterday]"
"Web3 政策 合规"
"数字货币 法规"
```

**市场行情**:
```
"比特币 价格 [昨日日期]"
"加密货币 市值 [yesterday]"
"BTC ETH 行情"
"加密市场 涨跌"
```

**采集目标**：每个类别3-5条，总计15-20条资讯

---

### Step 2: 智能翻译与筛选

#### 翻译规则

参考 [references/glossary.md](references/glossary.md) 的术语对照表。

**保留英文的术语**：
- DeFi、NFT、DAO、GameFi、Layer2、ZK
- 项目名称：Uniswap、Aave、OpenSea等
- 协议名称：Optimism、Arbitrum等

**翻译示例**：
- ❌ "Uniswap推出V4版本，引入了钩子功能"
- ✅ "Uniswap（去中心化交易所）推出V4版本，引入Hooks（钩子）功能"

**首次出现加注释**：
```
Optimistic Rollup（乐观卷叠）是一种Layer2扩容方案...
```

**数字格式化**：
- 金额：1000万美元、10亿美元
- 价格：比特币42,358.67美元
- 涨跌：上涨5.2%

#### 筛选标准

**高优先级（必选）**：
- 主流公链重大升级
- 知名项目融资(>1000万美元)
- 重大监管政策
- 头部交易所/协议重大事件
- 安全事件

**中优先级（选择性）**：
- 新项目发布（知名团队背书）
- 市场数据重大变化
- 生态合作动态

**低优先级（可忽略）**：
- 小额融资(<100万美元)
- 未验证传闻
- 纯营销内容
- Meme币炒作

**输出格式**：
```json
{
  "news": [
    {
      "category": "DeFi动态",
      "title": "Uniswap V4主网上线，引入自定义Hooks功能",
      "summary": "允许开发者定制交易逻辑，预计Gas费降低30%",
      "source": "The Block",
      "importance": "high"
    },
    ...
  ]
}
```

---

### Step 3: 热门话题选择

从采集的资讯中，使用AI分析选择一个最有价值的话题作为深度专题。

**选择标准**：
1. **热度高**：多个媒体报道、社交媒体讨论多
2. **影响大**：对Web3行业有重要意义
3. **深度价值**：有足够信息支撑800-1200字分析
4. **时效性**：近期发生的重要事件

**AI分析提示词**：
```
分析以下Web3资讯，选择最适合作为深度专题的话题：

[资讯列表]

选择标准：
1. 热度和影响力
2. 可展开深度分析
3. 对读者有价值

返回JSON：
{
  "topic": "选定的话题",
  "reason": "选择原因",
  "keywords": ["关键词1", "关键词2"],
  "related_news": ["相关资讯编号"]
}
```

---

### Step 4: 深度专题生成

针对选定话题，生成800-1200字的深度分析文章。

**文章结构**：

```markdown
## [话题标题]

### 📊 事件背景
（200-300字）
- 事件发生的背景
- 为什么重要
- 相关数据

### 🔍 深度解析
（400-500字）
- 技术原理分析
- 市场影响评估
- 行业意义解读
- 与其他项目/事件对比
- 引用专家观点（如有）

### 💡 趋势展望
（200-300字）
- 未来发展方向
- 可能的影响
- 对用户/投资者的建议
```

**写作要求**：

| 维度 | 要求 |
|------|------|
| 专业性 | 准确使用术语，数据有来源 |
| 深度 | 不停留表面，有独到见解 |
| 逻辑性 | 论证严密，层次分明 |
| 可读性 | 专业但不晦涩，有案例 |
| 客观性 | 不盲目鼓吹，也不过度悲观 |
| 术语 | DeFi/NFT/DAO等保留英文 |

**提升深度的要素**：
1. **数据支撑**：具体数字、同比环比、市场份额
2. **多维分析**：技术、市场、监管、用户多角度
3. **对比分析**：与竞品、历史数据对比
4. **趋势预判**：基于逻辑的未来展望
5. **案例支撑**：具体项目、用户案例

---

### Step 5: HTML格式化

将资讯和深度专题格式化为HTML，插入品牌素材。

**HTML结构**：

```html
<!-- 日期卡片 -->
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); ...">
  X月X日 Web3日报
  农历XX XX
</div>

<!-- 深度专题 -->
<div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); ...">
  🔥 深度专题
</div>
<div style="background: #f8f9fa; ...">
  [深度专题内容]
</div>

<!-- 今日要闻 -->
<div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); ...">
  📰 今日要闻
</div>

<!-- 区块链技术 -->
<div>
  <div style="color: #667eea;">⛓️ 区块链技术</div>
  <div>01. [新闻标题] - [摘要]</div>
  ...
</div>

<!-- DeFi动态 -->
<div>
  <div style="color: #f093fb;">💰 DeFi动态</div>
  <div>01. [新闻标题] - [摘要]</div>
  ...
</div>

<!-- NFT市场 -->
<div>
  <div style="color: #4facfe;">🎨 NFT市场</div>
  <div>01. [新闻标题] - [摘要]</div>
  ...
</div>

<!-- 监管政策 -->
<div>
  <div style="color: #fa709a;">⚖️ 监管政策</div>
  <div>01. [新闻标题] - [摘要]</div>
  ...
</div>

<!-- 市场行情 -->
<div>
  <div style="color: #30cfd0;">📈 市场行情</div>
  <div>01. [新闻标题] - [摘要]</div>
  ...
</div>

<!-- 每日一语 -->
<div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); ...">
  💡 每日一语<br>
  Web3的未来不是炒作，而是真正的价值创造和用户主权回归。
</div>
```

**配色方案**：

| 类别 | 颜色 | 图标 |
|------|------|------|
| 区块链技术 | #667eea (紫蓝) | ⛓️ |
| DeFi动态 | #f093fb (粉紫) | 💰 |
| NFT市场 | #4facfe (天蓝) | 🎨 |
| 监管政策 | #fa709a (粉红) | ⚖️ |
| 市场行情 | #30cfd0 (青色) | 📈 |

---

### Step 6: 封面图生成

使用豆包SeeDream API或OpenRouter Gemini生成封面图。

```bash
python3 ~/.claude/skills/web3-daily/web3-daily/scripts/generate_image.py cover \
  --title "X月X日Web3日报" \
  --style "tech" \
  --size 2048x2048
```

**提示词模板**：
```
Web3 daily news cover, date "[日期]", cyberpunk tech style,
blockchain network visualization, digital nodes, gradient purple blue,
neon cyan accents, futuristic, professional, clean composition,
high-tech aesthetic, 2048x2048px --v 6
```

**风格选项**：
- `tech`: 科技风（推荐，适合Web3主题）
- `modern`: 现代杂志风
- `minimalist`: 极简风

**注意**：图片尺寸必须至少3686400像素（推荐2048x2048）

---

### Step 7: 保存到Obsidian

保存Markdown版本用于归档和备份。

**保存路径**：`~/Documents/Obsidian/Web3日报/`

**文件命名**：`[YYYY-MM-DD]_Web3日报.md`

**文件格式**：
```markdown
---
title: X月X日Web3日报
date: YYYY-MM-DD
type: Web3日报
word_count: XXXX
categories: [区块链技术, DeFi, NFT, 监管, 行情]
tags: [Web3, 区块链, DeFi, NFT]
---

# X月X日Web3日报

## 🔥 深度专题

[深度专题内容]

## 📰 今日要闻

### ⛓️ 区块链技术
1. ...
2. ...

### 💰 DeFi动态
1. ...
2. ...

### 🎨 NFT市场
1. ...
2. ...

### ⚖️ 监管政策
1. ...
2. ...

### 📈 市场行情
1. ...
2. ...

---

💡 **每日一语**: Web3的未来不是炒作，而是真正的价值创造和用户主权回归。
```

---

### Step 8: 发布到微信公众号

使用微绿流量宝API发布到"三更Web3"公众号草稿箱。

**公众号信息**：

| 项目 | 值 |
|------|-----|
| 公众号名称 | 三更Web3 |
| API Key | `xhs_fff41080b1861be192872e9cd62399a0` |
| AppID | `${WECHAT_APP_ID}` |

**发布参数**：
```json
{
  "appid": "WEB3_WECHAT_APPID",
  "title": "X月X日Web3日报",
  "content": "[HTML内容]",
  "digest": "今日深度：[话题]；要闻：区块链技术、DeFi、NFT、监管、行情",
  "contentFormat": "html",
  "type": "news",
  "cover_image": "[封面图URL]"
}
```

**API端点**：`https://wlllb.com/api/wx/article`

---

## 环境变量配置

| 变量名 | 必需 | 说明 | 默认值 |
|--------|------|------|--------|
| `WECHAT_API_KEY` | ✅ | 微绿流量宝API Key | xhs_fff41080b1861be192872e9cd62399a0 |
| `WEB3_WECHAT_APPID` | ✅ | 三更Web3公众号AppID | 需配置 |
| `DOUBAO_API_KEY` | ✅* | 豆包API Key（备用） | - |

> *至少需要设置其中一个

**配置方法**：
```bash
# 编辑 ~/.zshrc
export WECHAT_API_KEY="xhs_fff41080b1861be192872e9cd62399a0"
export WEB3_WECHAT_APPID="wx_your_appid_here"
export DOUBAO_API_KEY="your_key_here"

# 使配置生效
source ~/.zshrc
```

---

## 使用示例

### 示例1：生成今日Web3日报

**用户**："生成今日Web3日报"

**执行流程**：
1. 环境检查
2. 采集昨天的Web3资讯（中英文）
3. 翻译并筛选15-20条要闻
4. 选择热门话题
5. 生成800-1200字深度专题
6. HTML格式化
7. 生成封面图
8. 保存到Obsidian
9. 发布到公众号

### 示例2：指定话题深度分析

**用户**："写一篇关于以太坊Layer2竞争格局的Web3日报"

**执行流程**：
1. 搜集Layer2相关资讯
2. 深度专题聚焦Layer2竞争（Optimism vs Arbitrum vs zkSync等）
3. 其余流程相同

### 示例3：试运行不发布

**用户**："生成Web3日报，试运行不发布"

**执行**：
```bash
python3 ~/.claude/skills/web3-daily/web3-daily/scripts/auto_web3_daily.py --dry-run
```

---

## 定时任务配置

使用GitHub Actions定时触发（每天中午12:00）。

### GitHub Actions配置

创建 `.github/workflows/web3-daily.yml`：

```yaml
name: Web3 Daily
on:
  schedule:
    - cron: '0 4 * * *'  # UTC 04:00 = 北京时间 12:00
  workflow_dispatch:

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install zhdate certifi requests

      - name: Run Web3 daily
        env:
          WECHAT_API_KEY: ${{ secrets.WECHAT_API_KEY }}
          WEB3_WECHAT_APPID: ${{ secrets.WEB3_WECHAT_APPID }}
        run: |
          # 实际需要通过Claude运行完整流程
          echo "Web3 Daily task triggered"
```

### macOS LaunchAgent（本地定时）

创建 `~/Library/LaunchAgents/com.user.web3-daily.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.web3-daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd ~/.claude/skills/web3-daily/web3-daily && claude run "生成今日Web3日报"</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>12</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/web3-daily.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/web3-daily.error.log</string>
</dict>
</plist>
```

**加载定时任务**：
```bash
launchctl load ~/Library/LaunchAgents/com.user.web3-daily.plist
```

---

## 质量检查清单

发布前确认：

- [ ] 采集15-20条权威资讯
- [ ] 英文资讯已翻译成中文
- [ ] 专业术语处理正确（DeFi/NFT保留英文）
- [ ] 深度专题字数800-1200字
- [ ] 深度专题有数据支撑和案例
- [ ] HTML格式渲染正确
- [ ] 五个分类各有2-5条资讯
- [ ] 封面图已成功生成（尺寸≥2048x2048）
- [ ] 内容客观中立，无夸大炒作
- [ ] 已保存到Obsidian备份

---

## 故障排查

### 问题1：环境变量未设置

**症状**：`错误: 未设置 WEB3_WECHAT_APPID 环境变量`

**解决**：
```bash
# 检查环境变量
echo $WEB3_WECHAT_APPID

# 设置环境变量
export WEB3_WECHAT_APPID="wx_your_appid"

# 永久设置：编辑 ~/.zshrc
echo 'export WEB3_WECHAT_APPID="wx_your_appid"' >> ~/.zshrc
source ~/.zshrc
```

### 问题2：WebSearch结果不足

**症状**：搜索返回的资讯数量少于15条

**解决**：
1. 扩大搜索时间范围（昨天→近3天）
2. 使用更广泛的搜索词
3. 增加搜索的媒体来源
4. 降低筛选标准

### 问题3：翻译术语不准确

**症状**：专业术语被错误翻译

**解决**：
1. 参考 `references/glossary.md` 术语对照表
2. 在提示词中明确保留英文的术语列表
3. 人工审核并修正

### 问题4：封面图生成失败

**症状**：`封面图生成失败`

**解决**：
1. 检查API Key：`echo $DOUBAO_API_KEY`
2. 检查网络连接
3. 尝试手动生成：
   ```bash
   python3 scripts/generate_image.py cover \
     --title "测试封面" --style "tech" --size 2048x2048
   ```
4. 文章可继续发布（无封面图）

### 问题5：发布失败

**症状**：`发布失败`

**解决**：
1. 检查API Key和AppID
2. 检查HTML格式是否正确
3. 检查内容长度（微信有限制）
4. 查看API返回的错误信息
5. 手动复制内容到公众号后台

---

## 最佳实践

### 资讯采集

- **优先搜索权威媒体**：使用媒体名称+日期精准搜索
- **交叉验证**：同一新闻多个来源时优先采用
- **时效性优先**：昨天的新闻>旧闻
- **避免炒作内容**：不收录纯营销、Meme币炒作

### 翻译规范

- **保留专业术语**：DeFi、NFT、DAO、Layer2等
- **首次出现加注释**："Optimistic Rollup（乐观卷叠）"
- **项目名称保留英文**："Uniswap（去中心化交易所）"
- **数字本地化**：1000万美元、上涨5.2%

### 深度专题

- **选题标准**：热度高、影响大、能展开分析
- **数据支撑**：引用具体数字和来源
- **多维分析**：技术、市场、监管多角度
- **案例丰富**：提供具体项目案例
- **客观中立**：不盲目鼓吹也不过度悲观

### 内容呈现

- **分类清晰**：5大类别逻辑分明
- **标题吸引**：简洁有力，突出价值点
- **格式统一**：编号、颜色、样式一致
- **视觉友好**：渐变卡片、图标、留白

---

## 相关技能

- [daily-tech-news](../daily-tech-news/SKILL.md) - AI科技财经日报
- [ai-edu-publisher](../ai-edu-publisher/SKILL.md) - AI教育资讯发布
- [wechat-publisher](../wechat-publisher/SKILL.md) - 微信公众号发布

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0 | 2026-01-30 | 初始版本，支持中英文采集、智能翻译、混合内容、自动发布 |
