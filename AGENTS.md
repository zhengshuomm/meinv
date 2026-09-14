# 美女品鉴中华美食短视频项目全局准则 (V5 纯中文提示词 + Veo 原生音画一体直出版)

欢迎来到中华美食 AI 短视频生成工作区。本项目专注于生产**“中国地方美食 + 高颜值中国美女”**的高完播率、真人电影质感 45 秒爆款短视频。

---

## 🚨 核心执行准则 (V5 升级版)

1. **技能自动挂载**：
   当用户提出任何美食短视频生成需求（如“帮我做武汉热干面”、“来个北京烤鸭的视频”、“生煎包视频方案”等），**必须无条件激活并遵照本工作区技能 [`chinese-beauty-food-video`](file:///.agents/skills/chinese-beauty-food-video/SKILL.md)** 与剪映自动化技能 **[`jianying-editor`](file:///.agents/skills/jianying-editor/SKILL.md)** 执行。

2. **提示词地道叙事与母语发音约束准则**：
   - **送给 Veo 等视频模型的生成提示词主体必须 100% 采用专业电影级地道中文**，坚决杜绝任何英文机位词；
   - 必须严格遵循六段式公式：`【1. 景别运镜】 + 【2. 锁定主角固定发型与服装】 + 【3. 面对镜头亲口说话口型生动自然】 + 【4. 食物微距诱人细节与吃法动作】 + 【5. 市井暖色烟火气】 + 【6. 严苛中文负向约束】`；
   - **末尾独立段落约束 (Mandatory Trailing Speech Paragraph)**：在出镜说话分镜提示词最后，必须单独另起一行追加独立段落，硬性规范汉语声调、变调、停顿节奏与母语发音：
     ```text
     Correct Mandarin lexical tones, tone changes, sentence rhythm, pauses, and emphasis. Her speech must sound natively Chinese, not like a foreigner speaking Chinese. Do not translate or alter the Chinese dialogue. No English speech.
     ```

3. **第一人称女主亲口说地道中文台词 (Veo 原生音画一体直出，彻底抛弃 lipsync)**：
   - 出镜美女主播面对镜头亲口说地道中文大白话，出镜说话分镜（Shot 1, 2, 5, 6）的中文提示词中，显式注入女主直视镜头张口说话与生动唇动指令；
   - **完全依赖 Veo 原生生成母语声音与口型**：在 Flow 中通过人物绑定（`@女主姓名`）配合末尾专属独立发音约束段，Veo 直接输出标准母语普通话发音、真实声调重音、生动面部唇动以及现场市井拟音（炭火微爆、热油滋啦、食客人声），**完全由 Veo 原生直出，彻底废弃任何外部 lipsync 工具（如 Wav2Lip 等）及剪映二次对口型**；
   - 台词严格控制在 **120～155 个汉字**（大白话、真诚、有态度），全篇**严禁使用“老饕”、“直撞天灵盖”、“治好所有内耗”等一切装腔作势、非正常现代口语的生僻辞藻或 AI 油腻套话**。

4. **14位女主三层物理强锁定 (杜绝换镜换脸换衣)**：
   - `references/character_roster_pool.json` 为全部 14 位女主全量配置永久不可变纯中文锚点：固定发型面部（`hair_face_anchor_cn`）、固定服装（`wardrobe_anchor_cn`）、口播风格（`speaking_style_cn`）与负向排斥词（`negative_prompt_cn`）；
   - 分镜生成器自动将中文锚点全量注入每个有女主的分镜，配合定妆参考图（`character_reference`）实现人脸、发型与服装强锁定。

5. **剪映自动化编排管线 (原生音画保留 + 毫秒级字幕对齐)**：
   - 挂载 `jianying-editor-skill`，通过 `scripts/export_to_jianying.py` 一键生成 9:16 (1080x1920) 剪映 Pro 竖屏草稿；
   - 自动化排布主视频轨（强制保留 Veo 原生音频 volume=1.0，含地道母语台词与市井现场环境音）与毫秒级时序对齐的大字字幕轨；
   - 零二次对口型负担：打开剪映即可直接预览完整视音频成品，可按需微垫背景轻音乐后直接一键导出。

6. **食物决定故事与 6 镜动态叙事**：
   - 严禁千篇一律的动作流水账，镜头完全由当前菜品特性动态推导；
   - 标准 6 镜架构：Shot 1 (0-4s Hook 亲口说) ➔ Shot 2 (4-10s Context 面对镜头介绍) ➔ Shot 3 (10-18s Process 制作高潮) ➔ Shot 4 (18-27s Secret 吃法细节) ➔ Shot 5 (27-37s Taste 咀嚼后对镜头点评) ➔ Shot 6 (37-45s Verdict 直视镜头金句收尾)。

7. **前置事实校验与高通用性**：
   - 脚本立项前必须确认地道名称、核心配料、制作要诀、正统吃法；
   - 技能保持高度通用，支持全国任意城市、任意特色菜品与 14 位女主自适应匹配。

---

## 🛠️ 核心工具链
- **动态分镜与项目脚手架**：`.agents/skills/chinese-beauty-food-video/scripts/food_project_factory.py`
- **剪映 Pro 竖屏草稿与自动化编排导出器**：`.agents/skills/chinese-beauty-food-video/scripts/export_to_jianying.py`
- **自然脚本生成与去 AI 腔打磨**：`.agents/skills/chinese-beauty-food-video/scripts/script_refiner.py`
- **动态 Chrome CDP 自动化控制器**：`.agents/skills/chinese-beauty-food-video/scripts/flow_cdp_controller.py`
- **本地直接合成管线 (备选)**：`.agents/skills/chinese-beauty-food-video/scripts/assemble_food_video.py`
- **剪映自动化引擎**：`.agents/skills/jianying-editor/scripts/jy_wrapper.py`
