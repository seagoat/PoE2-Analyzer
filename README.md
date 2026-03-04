# PoE2 Analyzer (流放之路2 构筑与连锁分析器)

这是一个针对 Path of Exile 2 (流放之路2) 开发的独立轻量级辅助工具。
它可以帮助玩家通过可视化的方式探索技能、天赋与暗金装备之间极其复杂的“连锁反应”与“数值乘区”。

## 🌟 核心功能

1. **三栏式节点探索器 (Node Explorer)**
   - 输入任意技能、天赋或装备，自动拆解其**前置触发条件**与**后续增益影响**。
   - 左侧展示“谁能触发/增幅我”，右侧展示“我能触发/增幅谁”。
   - 支持跨节点点击穿透，顺藤摸瓜寻找终极 BD 思路。

2. **装备纸娃娃沙盒 (Build Sandbox)**
   - 提供各部位的装备槽位 (头部、胸甲、戒指、武器等)。
   - 从探索器中一键将装备或天赋加入沙盒。
   - **实时伤害倍率计算器**：自动分离 \Increased\ (加法区) 和 \More\ (指数乘区)，并计算最终伤害放大倍率。

3. **全景动态辐射脑图 (Dynamic Force Graph)**
   - 将游戏中 5000+ 个节点与 50万+ 条隐性关联连线在 3D 物理引擎中渲染。
   - 采用瀑布流布局 (前置在左，后续在右)。
   - 双击节点引发“宇宙大爆炸”式的网状辐射扩展，最直观地寻找游戏中的核心“枢纽节点”。

## 📸 界面预览

*(请将你本地的截图保存到 \docs/images\ 目录下并替换以下链接)*

- **主探索界面与构筑沙盒:**
  ![主界面预览](./docs/images/main_sandbox.png)

- **全景动态脑图:**
  ![全景脑图预览](./docs/images/dynamic_graph.png)

## 🚀 如何运行

本工具为纯前端实现，结合 Python 数据提取脚本。你可以直接运行：

\\\ash
# Windows 用户
.\start_web.ps1

# Linux / Mac 用户
./start_web.sh
\\\

然后在浏览器中打开: [http://localhost:8000](http://localhost:8000)

## 🛠️ 数据更新说明

本工具的数据基于 PathOfBuilding (PoB) 社区版。如果你需要拉取最新的游戏数据：
1. 确保上级目录中存在 \PathOfBuilding-PoE2\ 源码。
2. 运行提取脚本：
   \\\ash
   cd tools
   python export_relations.py
   \\\

## 📝 技术栈
- 前端: 原生 HTML/JS, TailwindCSS, Force-Graph (D3.js)
- 后端/数据: Python 3 (正则文本解析)
