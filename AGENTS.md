# 美女品鉴中华美食短视频项目全局准则 (V2 动态工业版)

欢迎来到中华美食 AI 短视频生成工作区。本项目专注于生产**“中国地方美食 + 高颜值中国美女”**的高完播率、真人电影质感 45 秒爆款短视频。

---

## 🚨 核心执行准则 (V2 全新升级)

1. **技能自动挂载**：
   当用户提出任何美食短视频生成需求（如“帮我做武汉热干面”、“来个北京烤鸭的视频”、“生煎包视频方案”等），**必须无条件激活并遵照本工作区技能 [`chinese-beauty-food-video`](file:///.agents/skills/chinese-beauty-food-video/SKILL.md)** 执行。

2. **食物决定故事，严禁固定动作模板**：
   - 彻底废除固定动作流水账（严禁每条都预设卷饼、抽签、咬第一口、喝汽水等）；
   - **固定的是叙事功能，具体动作必须由当前城市与美食特性动态生成**：
     - **Shot 1 (0~4s) Hook**：阻止划走，一个强视觉事件 + 真实情绪 + 一句干脆短台词；
     - **Shot 2 (4~10s) Context**：城市烟火气与特色环境交代，人物自然融入；
     - **Shot 3 (10~18s) Process**：当前菜品最具辨识度的制作高潮（如爆炒、拌酱、片鸭、揭锅）；
     - **Shot 4 (18~27s) Secret**：特色吃法细节、火候秘密与内部质感；
     - **Shot 5 (27~37s) Taste**：女主真正品尝，真实咀嚼微表情，具体味觉解构，拒绝浮夸大瞪眼；
     - **Shot 6 (37~45s) Verdict**：有记忆点、有讨论空间的城市金句与从容收尾。

3. **6 镜精简与生成风险控制**：
   - 默认采用 **6 个独立生成 clip（每镜 6～8 秒）**，杜绝过度切镜导致的换脸、换衣、手部畸变与环境漂移；
   - 始终坚持“食物 40% + 人物 25% + 动作 20% + 环境 15%”的视觉重心，美女是流量入口，美食是内容灵魂。

4. **多维资产锚定与 Continuity Router 连续性路由**：
   - **Reference > 长篇文字重复描述**：依托人物参考图（`character_reference`）实现人脸、发型、妆容与服装强锁定，避免文字喧宾夺主；
   - **严禁无脑链式末帧继承**：只有在相同场景且构图相近的连续动作时才继承上一镜末帧；当景别从人物大跳至食材微距或环境时，路由至对应的 `food_reference` 或 `character_reference`。

5. **真人口语化旁白与 TTS 解耦架构**：
   - **字数精准控制**：45 秒旁白严格控制在 **120～155 个汉字**，严禁超速报菜名；
   - **去 AI 腔**：全篇最多允许 1～2 个金句 punch line，其余必须是具体、真实、接地气的味觉描述；
   - **解耦流水线**：先写好脚本 ➔ TTS 试读获取真实音频波形与时间戳 ➔ 匹配分镜时间轴 ➔ 视频生成 ➔ 音画智能闪避合流。

6. **前置事实校验 (Food Research)**：
   - 脚本立项前必须确认地道名称、属地、核心配料、制作要诀、当地正统吃法与禁忌，严禁瞎编乱造引发当地食客争议。

7. **视频执行引擎：Chrome CDP + Playwright 自动化**：
   - 复用本地 Chrome 调试端口（`localhost:9222`）驱动 Google Flow 画布，支持动态分镜解析、9:16 竖屏校准、剪贴板参考图注入与异常捕获。

---

## 🛠️ 核心工具链
- **动态分镜与项目脚手架**：`.agents/skills/chinese-beauty-food-video/scripts/food_project_factory.py`
- **自然脚本生成与去 AI 腔打磨**：`.agents/skills/chinese-beauty-food-video/scripts/script_refiner.py`
- **动态 Chrome CDP 自动化控制器**：`.agents/skills/chinese-beauty-food-video/scripts/flow_cdp_controller.py`
- **全要素自动化质检**：`.agents/skills/chinese-beauty-food-video/scripts/audio_visual_validator.py`
