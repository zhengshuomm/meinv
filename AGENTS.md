# 美女品鉴中华美食短视频项目全局准则 (V4 纯中文提示词 + 地道中文语音 + 剪映对口型版)

欢迎来到中华美食 AI 短视频生成工作区。本项目专注于生产**“中国地方美食 + 高颜值中国美女”**的高完播率、真人电影质感 45 秒爆款短视频。

---

## 🚨 核心执行准则 (V4 升级版)

1. **技能自动挂载**：
   当用户提出任何美食短视频生成需求（如“帮我做武汉热干面”、“来个北京烤鸭的视频”、“生煎包视频方案”等），**必须无条件激活并遵照本工作区技能 [`chinese-beauty-food-video`](file:///.agents/skills/chinese-beauty-food-video/SKILL.md)** 与剪映自动化技能 **[`jianying-editor`](file:///.agents/skills/jianying-editor/SKILL.md)** 执行。

2. **提示词 100% 纯中文铁律 (坚决杜绝任何英文提示词)**：
   - **送给 Veo 等视频模型的生成提示词 (`prompt`) 必须 100% 采用专业电影级纯中文**，坚决杜绝任何英文输入或英文机位词；
   - 必须严格遵循纯中文六段式公式：`【1. 景别运镜】 + 【2. 锁定主角固定发型与服装】 + 【3. 面对镜头亲口说话口型生动自然】 + 【4. 食物微距诱人细节与吃法动作】 + 【5. 市井暖色烟火气】 + 【6. 严苛中文负向约束】`。

3. **第一人称女主亲口说地道中文台词 (拒绝画外音旁白，彻底根除洋腔)**：
   - 出镜美女主播面对镜头亲口说地道中文大白话，出镜说话分镜（Shot 1, 2, 5, 6）的中文提示词中，必须显式注入女主直视镜头张口说话与生动唇动指令：`“女主直接抬眸直视摄像机镜头，眼神自信灵动，嘴唇自然饱满开合，清晰说出地道中文台词，口型动作生动真实，面部微表情随说话起伏...”`；
   - **彻底根除洋腔与听不懂**：Veo 是画面扩散模型而非中文语音模型，Veo 原生伴生音频必为带欧美口音的伪中文乱语。因此视频轨音频必须强制设为 0（静音），台词语音 100% 由中国母语语音引擎（剪映 Pro 原生音色库 / Edge-TTS）提供；
   - 台词严格控制在 **120～155 个汉字**（大白话、真诚、有态度），全篇**严禁使用“老饕”、“直撞天灵盖”、“治好所有内耗”等一切装腔作势、非正常现代口语的生僻辞藻或 AI 油腻套话**。

4. **14位女主三层物理强锁定 (杜绝换镜换脸换衣)**：
   - `references/character_roster_pool.json` 为全部 14 位女主全量配置永久不可变纯中文锚点：固定发型面部（`hair_face_anchor_cn`）、固定服装（`wardrobe_anchor_cn`）、口播风格（`speaking_style_cn`）与负向排斥词（`negative_prompt_cn`）；
   - 分镜生成器自动将中文锚点全量注入每个有女主的分镜，配合定妆参考图（`character_reference`）实现人脸、发型与服装强锁定。

5. **剪映自动化管线与智能对口型合流**：
   - 挂载 `jianying-editor-skill`，通过 `scripts/export_to_jianying.py` 一键生成 9:16 (1080x1920) 剪映 Pro 竖屏草稿；
   - 自动化排布主视频轨（强制 volume=0 静音消除洋腔）、女主地道中文口播音频轨与毫秒级对齐的大字字幕轨；
   - 在剪映 Pro 中右键点击视频片段选择**「智能对口型」**，调用剪映官方中文唇形同步引擎实现 100% 真实母语发音与音画唇动精准贴合。

6. **食物决定故事与 6 镜动态叙事**：
   - 严禁千篇一律的动作流水账，镜头完全由当前菜品特性动态推导；
   - 标准 6 镜架构：Shot 1 (0-4s Hook 亲口说) ➔ Shot 2 (4-10s Context 面对镜头介绍) ➔ Shot 3 (10-18s Process 制作高潮) ➔ Shot 4 (18-27s Secret 吃法细节) ➔ Shot 5 (27-37s Taste 咀嚼后对镜头点评) ➔ Shot 6 (37-45s Verdict 直视镜头金句收尾)。

7. **前置事实校验与高通用性**：
   - 脚本立项前必须确认地道名称、核心配料、制作要诀、正统吃法；
   - 技能保持高度通用，支持全国任意城市、任意特色菜品与 14 位女主自适应匹配。

---

## 🛠️ 核心工具链
- **动态分镜与项目脚手架 (V3 英文提示词+口播版)**：`.agents/skills/chinese-beauty-food-video/scripts/food_project_factory.py`
- **剪映 Pro 竖屏草稿与智能对口型导出器**：`.agents/skills/chinese-beauty-food-video/scripts/export_to_jianying.py`
- **自然脚本生成与去 AI 腔打磨**：`.agents/skills/chinese-beauty-food-video/scripts/script_refiner.py`
- **动态 Chrome CDP 自动化控制器**：`.agents/skills/chinese-beauty-food-video/scripts/flow_cdp_controller.py`
- **本地直接合成管线 (备选)**：`.agents/skills/chinese-beauty-food-video/scripts/assemble_food_video.py`
- **剪映自动化引擎**：`.agents/skills/jianying-editor/scripts/jy_wrapper.py`
