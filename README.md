# 美女品鉴中华美食短视频全自动生产工程 (V2 动态工业版)

本项目是一个专注于生产**“中国地方美食 + 高颜值中国美女”**的高完播率、真人电影质感 45 秒竖屏爆款短视频的全自动化工业级方案。

全套方案基于 **Google Flow + Chrome CDP + Playwright 自动化执行链路**，彻底告别单一套路模板，实现由食物特性驱动的动态分镜、自然口语化旁白与 Continuity Router 智能连续性路由。

---

## 🌟 V2 核心升级特色

1. **食物决定故事，告别固定动作模板**：
   - 彻底废除预设动作流水账；根据不同地方菜系（热干面、生煎、烤鸭、火锅、螺蛳粉等）的制作高潮与吃法规矩，自适应规划动态镜头。
2. **6 镜精简与风险控制 (Clip-by-Clip Stability)**：
   - 默认精简为 **6 个高质感独立生成 clip（每镜 6～8 秒）**，极大降低多轮生成导致的换脸、换衣服、手部畸变与环境漂移概率。
3. **Reference > 冗长文字描述 & Continuity Router 连续性路由**：
   - 依托高清人物定妆参考图锁定容貌与服饰，提示词不再堆砌冗余外貌词；
   - 杜绝无脑链式末帧继承。通过 Continuity Router 区分动作连续（继承末帧）、特写切回人物（重定向锚定）与食材微距（食物参考），构图与连续性完全解耦。
4. **真人生活化旁白与去 AI 腔**：
   - 45 秒全片严格控制在 **120～155 个汉字**；
   - 全片最多允许 1～2 个爆点金句，其余全部为接地气、真实的味觉与火候描述，坚决剔除“天灵盖”、“治好内耗”、“直接沉默”等 AI 网红套话。
5. **前置美食事实校验 (Food Research)**：
   - 正式分镜前必须建立 `food_profile`，校验正统名称、属地、关键食材、制作工序与不可出现错误，确保内容经得起当地食客检验。
6. **音画解耦流水线**：
   - 旁白先行 ➔ TTS 生成真实时间戳 ➔ 匹配分镜时间轴 ➔ 视频生成 ➔ 声音四层混音与 BGM 智能闪避。

---

## 📁 项目结构

```text
meinv/
├── AGENTS.md                  # 全局工作区准则与执行规范 (V2 版)
├── .agents/skills/            # 核心技能与工业级工具链
│   └── chinese-beauty-food-video/
│       ├── SKILL.md           # 技能核心标准说明书 (V2 动态版)
│       ├── references/        # 角色档案库、提示词公式、地域风味库
│       ├── scripts/           # CDP 控制器、脚手架、质检脚本、台词打磨工具
│       └── examples/          # 潮汕生腌、兰州拉面、重庆小面等范例
├── assets/                    # 项目资源
│   └── character_master/      # 14 位预设高颜值女主全套高清定妆图
├── examples/                  # 动态工程配置文件 (如热干面、生煎、淄博烧烤等)
├── README.md
└── .gitignore
```

---

## 🚀 快速上手

### 1. 启动 Chrome 调试端口
在本地 macOS 启动带有调试端口的 Chrome 浏览器：
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/Users/$(whoami)/chrome_dev_profile"
```

### 2. 生成全新地方美食 V2 工程配置 (例: 武汉热干面)
```bash
python3 .agents/skills/chinese-beauty-food-video/scripts/food_project_factory.py --food "热干面" --city "武汉" --character "沈昭"
```

### 3. 查看分镜清单与状态
```bash
python3 .agents/skills/chinese-beauty-food-video/scripts/flow_cdp_controller.py --config examples/热干面_v2_45s.json --list
```

### 4. 自动化运行 Flow 视频生成
```bash
# 生成单镜 (如 Shot 1 黄金钩子)
python3 .agents/skills/chinese-beauty-food-video/scripts/flow_cdp_controller.py --config examples/热干面_v2_45s.json --shot 1

# 批量生成全部 6 镜
python3 .agents/skills/chinese-beauty-food-video/scripts/flow_cdp_controller.py --config examples/热干面_v2_45s.json --all
```

---

## 📜 规范说明
本项目立足于弘扬中华传统地方饮食文化，所有工程配置与提示词均遵循 100% 纯中文标准。
