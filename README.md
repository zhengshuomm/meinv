# 美女品鉴中华美食短视频全自动生产工程 (100% 纯中文版)

本项目是一个专注于生产**“中国美女吃中国美食”**的高完播率、真人电影质感 45 秒竖屏爆款短视频的全自动化工业级方案。

基于 **Google Flow + Chrome CDP + Playwright 无感免密自动化链路**，结合严格的提示词工程与首尾帧链式强锚定，彻底解决 AI 视频人物换脸、换衣服与叙事断层问题。

---

## 🌟 核心特色与三大技术红线

1. **黄金 3 秒美女首击抓人定律**：
   - 严禁纯食物空景开场！第 1 镜头必须【高颜值中国美女 + 滚烫美食大口咬下 + 肉汁爆开 + 眼神震惊放大】四位一体同时登场，瞬间拉满完播率。
2. **每镜全貌与衣着强制锁定**：
   - 绝不使用模糊泛化代词。每个出镜镜头最前方强制注入女主完整外貌与特定服饰前缀，负向词拦截“更换衣服、换脸变脸、散发”。
3. **单向递进叙事连贯性法则**：
   - 严格遵循“第一口爆汁震撼入场 ➔ 坐定介绍 ➔ 眼前炉火 ➔ 亲手卷饼 ➔ 抽签动作 ➔ 沉浸大嚼 ➔ 爽饮升华 ➔ 眼神杀收尾”单向不可逆时间线。
4. **Chrome CDP 自动化生成引擎**：
   - 复用本地已登录 Google 账号的 Chrome 实例（`localhost:9222`），无需 API Key、无需逆向登录，原生支持 9:16 画布、剪贴板强注入起跑首帧与毫秒级抓取。

---

## 📁 项目结构

```text
meinv/
├── AGENTS.md                  # 全局工作区准则与执行规范
├── .agents/skills/            # 核心技能与工业级工具链
│   └── chinese-beauty-food-video/
│       ├── SKILL.md           # 技能核心流程规范
│       ├── references/        # 角色档案库、提示词公式、地域风味库
│       ├── scripts/           # CDP 控制器、脚手架、质检脚本
│       └── examples/          # 潮汕生腌、兰州拉面、重庆小面等范例
├── assets/                    # 项目资源
│   └── character_master/      # 预设高颜值女主全套高清定妆图
├── examples/                  # 完整生成工程样例（如淄博烧烤 45s 案）
└── .gitignore
```

---

## 🚀 快速上手

### 1. 启动 Chrome 调试端口
在本地 macOS 启动带有调试端口的 Chrome 浏览器：
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/Users/$(whoami)/chrome_dev_profile"
```

### 2. 运行 Flow 自动化视频生成
```bash
python3 .agents/skills/chinese-beauty-food-video/scripts/flow_cdp_controller.py examples/zibo_shaokao_45s.json
```

---

## 📜 许可与规范
本项目立足于弘扬中华传统美食文化，所有工程配置与提示词均采用纯中文标准。
