# 三更Web3品牌素材说明

本目录存放"三更Web3"公众号的品牌视觉素材。

## 目录结构

```
brand-materials/
├── title-banner/        # 标题栏图片
│   └── web3-title.gif   # 文章顶部标题栏动图
├── footer/              # 尾标图片
│   └── web3-footer.gif  # 文章底部尾标动图
└── qrcode/              # 二维码
    └── web3-qrcode.png  # 公众号二维码
```

## 设计规范

### 1. 标题栏 (web3-title.gif)
- **尺寸**: 900x200px
- **风格**: 赛博朋克科技风
- **配色**:
  - 主色：渐变紫蓝 (#667eea → #764ba2)
  - 辅助色：霓虹青色 (#00f2fe)
- **元素**:
  - 左侧："三更Web3"品牌名
  - 右侧：区块链/Web3视觉符号（链条、节点、加密符号）
  - 背景：流动的数字粒子动效
- **文字**: "三更Web3·每日洞察" 或 "Web3 Daily Insights"

### 2. 尾标 (web3-footer.gif)
- **尺寸**: 600x150px
- **风格**: 简约现代
- **配色**: 与标题栏呼应
- **元素**:
  - "用智慧拥抱Web3未来" 或类似slogan
  - 简洁的区块链图标
  - 轻微动效（闪烁/流动）

### 3. 二维码 (web3-qrcode.png)
- **尺寸**: 500x500px
- **样式**:
  - 中心：公众号二维码
  - 外框：渐变边框 (#667eea → #00f2fe)
  - 底部：引导文案 "关注三更Web3，每日洞察区块链"

## 使用位置

```html
<!-- 文章开头 -->
<img src="title-banner/web3-title.gif" style="width: 100%; margin-bottom: 20px;">

<!-- 文章内容 -->
...

<!-- 文章结尾 -->
<img src="footer/web3-footer.gif" style="width: 80%; margin: 30px auto; display: block;">

<!-- 底部二维码 -->
<div style="text-align: center; margin-top: 30px;">
  <p style="font-size: 16px; color: #666;">关注我们，获取每日Web3洞察</p>
  <img src="qrcode/web3-qrcode.png" style="width: 200px;">
</div>
```

## 制作建议

可使用以下工具制作：
- **设计软件**: Figma / Adobe Illustrator / Canva
- **GIF动画**: Photoshop / After Effects / ezgif.com
- **AI生成**: Midjourney / Stable Diffusion（提示词见下）

### Midjourney 提示词参考

**标题栏**:
```
"San Geng Web3" title banner, cyberpunk tech style, gradient purple to blue background,
blockchain nodes, digital particles flowing, neon cyan accents, modern sans-serif typography,
900x200px, animated GIF style, futuristic, professional --ar 9:2 --v 6
```

**尾标**:
```
Web3 footer design, minimalist, "Embrace Web3 Future with Wisdom" text,
blockchain icon, gradient colors purple blue cyan, subtle glow animation,
600x150px, clean modern style --ar 4:1 --v 6
```

## 替代方案

如果暂无设计素材，可以：
1. **纯文字版**: 使用HTML渐变背景代替图片
2. **占位符**: 临时使用纯色卡片+文字
3. **外包设计**: 找设计师定制（预算约200-500元）

## 待办事项

- [ ] 设计并上传 web3-title.gif
- [ ] 设计并上传 web3-footer.gif
- [ ] 获取公众号二维码并上传 web3-qrcode.png
- [ ] 上传素材到图床获取稳定URL
- [ ] 更新 SKILL.md 中的素材路径
