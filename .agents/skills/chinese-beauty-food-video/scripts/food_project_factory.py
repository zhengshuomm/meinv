#!/usr/bin/env python3
"""
中华美食短视频工程立项脚手架 (V2 动态工业版)
执行链路：
Food Research (事实校验) 
  ➔ Creative Angle (核心创意角度) 
  ➔ Hook Generator (动态黄金钩子，8-16字) 
  ➔ Narration Writer (自然真实中文旁白，120-155字，1-2个Punchline，去AI腔) 
  ➔ Storyboard Planner (动态 6 镜分镜架构) 
  ➔ Reference Anchor & Prompt Builder (结构化权重提示词)
"""

import os
import sys
import json
import random
import argparse

WORKSPACE_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

def load_character_pool():
    pool_path = os.path.join(os.path.dirname(__file__), "..", "references", "character_roster_pool.json")
    if os.path.exists(pool_path):
        with open(pool_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("characters", [])
    return []

def select_character(pool, character_query=None, food_name=None, city=None):
    """根据食物、地域、风格自适应推荐女主"""
    if not pool:
        return {
            "character_id": "shen_zhao_yujie",
            "name": "沈昭",
            "style_label": "高冷老饕御姐风",
            "photo_path": "assets/character_master/shen_zhao_master.jpg",
            "visual_traits": "20岁，冷白皮，身材高挑172cm超模比例，修长身材，清冷高级下颌线，微挑猫眼，右眼角小泪痣，黑色高马尾，身穿黑色修身V领针织长裙配银色细锁骨链。",
            "personality": "高冷飒爽、懂行挑剔、极度自信、对美食毫不妥协，反差萌极强。",
            "voice_persona": {"voice_name": "zh-CN-XiaoxiaoNeural", "style": "cheerful", "rate": "+10%"},
            "expression_style": "毒舌犀利、一针见血、老饕黑话张口就来。"
        }
    
    if character_query:
        for char in pool:
            if character_query in char.get("name", "") or character_query == char.get("character_id", "") or character_query in char.get("style_label", ""):
                return char

    # 根据地域与食物匹配
    combined = f"{city or ''} {food_name or ''}"
    for char in pool:
        for match in char.get("best_match_cuisines", []):
            if match in combined:
                return char

    return random.choice(pool)

def conduct_food_research(food_name: str, city: str = "", province: str = ""):
    """Stage 1: 地方美食事实调研 (构建 food_profile)"""
    # 典型美食特征库内置兜底（支持根据传入的美食动态生成真实画像）
    known_database = {
        "热干面": {
            "canonical_name": "武汉热干面",
            "city": "武汉",
            "province": "湖北",
            "category": "特色面食 / 过早文化",
            "core_ingredients": ["碱水面（碱面提前掸过放凉）", "纯芝麻酱（小磨香油化开）", "辣萝卜丁", "酸豆角", "香葱", "生抽老抽", "少许蒜水"],
            "signature_process": ["沸水锅中大笊篱捞面几秒即起", "扣入纸碗甩净水分", "大勺淋上稠厚香浓的纯芝麻酱", "飞快撒入红亮辣萝卜丁与葱花"],
            "signature_eating_method": ["必须在30秒内用筷子上下飞速翻拌均匀", "让每一根粗面条均匀挂满浓酱", "趁热大口挑起吃"],
            "visual_highlights": ["捞面瞬间升腾的浓白水汽", "深褐色芝麻酱如绸缎般浇在黄色碱面上", "双手筷子翻飞快速拌匀的动感", "爽脆红萝卜丁"],
            "texture": ["面条扎实筋道微偏硬", "芝麻酱醇厚粘稠浓郁", "萝卜丁清脆解腻"],
            "flavor": ["浓郁复合芝麻坚果香", "咸鲜微辣微甜", "后味麦香回甘"],
            "cultural_context": "武汉人清晨‘过早’的精神图腾，边走边吃，雷厉风行。",
            "common_misconceptions": ["误以为是煮烂的挂面", "误以为放麻酱很多水会稀", "放陈醋或者花生酱（外地改版）"],
            "must_not_show": ["清汤面条", "面条软烂断裂", "优雅用刀叉吃", "长时间放置坨成面饼"]
        },
        "生煎": {
            "canonical_name": "上海生煎包（生煎馒头）",
            "city": "上海",
            "province": "上海",
            "category": "传统点心",
            "core_ingredients": ["半发酵面皮", "紧实猪肉馅（加入皮冻熬制高汤）", "香葱", "黑白芝麻", "菜籽油"],
            "signature_process": ["大平底生铁锅密密麻麻排满生煎", "油煎到底部微黄后泼水加盖焖熟", "揭开巨大木质锅盖瞬间水汽轰然腾起", "撒上大把碧绿葱花与炒香芝麻"],
            "signature_eating_method": ["先开窗后喝汤，轻轻咬开侧面上方小口，吹凉后先吸鲜甜肉汁，再蘸镇江香醋吃皮肉与焦底"],
            "visual_highlights": ["木锅盖揭开瞬间大团白雾与热油滋啦轰鸣", "平底铲起生煎时露出的金黄酥脆焦底", "咬破薄皮瞬间清亮高汤如琥珀流淌"],
            "texture": ["底部金黄硬脆焦香", "顶皮松软白嫩", "肉馅抱团弹牙", "汤汁滚烫鲜甜"],
            "flavor": ["鲜甜肉香", "焦香酥脆麦香", "葱香芝麻香交融"],
            "cultural_context": "上海弄堂烟火气的经典代表，排队等出锅的市井仪式感。",
            "common_misconceptions": ["直接整个大口咬下被烫得满嘴起泡喷溅", "底部烤焦发黑"],
            "must_not_show": ["汤汁无故爆炸喷射射中镜头", "用微波炉加热软塌塌的生煎", "里面没有汤汁干瘪的肉馅"]
        },
        "淄博烧烤": {
            "canonical_name": "淄博烧烤",
            "city": "淄博",
            "province": "山东",
            "category": "市井烧烤",
            "core_ingredients": ["散发麦香的山东手工薄面饼", "临淄嫩青白小葱", "秘制咸鲜甜面酱", "七分瘦三分肥现切炭烤五花肉与牛肉串"],
            "signature_process": ["师傅先在大火炉烤至七八成熟", "端上桌放在每桌专属双层红泥独立小炭炉上翻烤", "肉串滋啦冒出金色油花"],
            "signature_eating_method": ["左手拿薄饼对折沾上甜面酱，夹上一整根嫩小葱，包裹两三串刚离火的滚烫肉串，右手利落反手反抽铁签，整口吞嚼"],
            "visual_highlights": ["红泥独立炭炉红炭火星微爆", "面饼裹肉利落反手抽铁签的爽快瞬间", "小葱青翠与焦黄五花肉的色彩反差"],
            "texture": ["面饼麦香韧劲", "五花肉焦香外脆内爆油", "生小葱清甜脆嫩解腻"],
            "flavor": ["炭火焦香", "酱香甜咸", "葱香微辛带甘"],
            "cultural_context": "山东齐鲁大地的豪爽烟火气，围炉而坐的真诚与纯粹。",
            "common_misconceptions": ["直接撸串不卷饼", "用大葱而不是细嫩小葱", "不放甜面酱"],
            "must_not_show": ["电烤箱", "普通冷冻速冻肉串", "没有独立小烤炉"]
        }
    }

    # 优先使用数据库，否则基于输入动态组装标准数据结构
    matched = None
    for k, v in known_database.items():
        if k in food_name or food_name in k:
            matched = v.copy()
            break

    if not matched:
        matched = {
            "canonical_name": f"{city or ''}{food_name}",
            "city": city or "地方名城",
            "province": province or "地方",
            "category": "地道地方特色美食",
            "core_ingredients": [f"地道现做{food_name}核心主料", "秘制地域风味酱料", "新鲜当地佐料小菜"],
            "signature_process": [f"大锅热气翻滚现做{food_name}", "师傅熟练操作出锅瞬间热气氤氲", "趁热装盘淋上特调料汁"],
            "signature_eating_method": [f"趁刚出锅最热腾腾时品尝第一口，搭配当地特制蘸料"],
            "visual_highlights": [f"刚出锅升腾的白色热气", f"{food_name}金黄诱人的纹理与油润光泽", "用筷子夹起或盛起的细节特写"],
            "texture": ["外脆内嫩或筋道爽滑", "层次分明"],
            "flavor": ["地道鲜香浓郁", "地道本味回甘"],
            "cultural_context": f"{city or '当地'}市井烟火深处代代相传的地道滋味。",
            "common_misconceptions": ["误以为是工业预制菜", "非当地正统搭配吃法"],
            "must_not_show": ["冷冰冰无热气", "机器流水线质感", "违背当地正统吃法的手法"]
        }
    return matched

def plan_creative_angle(food_profile: dict, tone_preference: str = None) -> str:
    """Stage 2: 创意角度决策"""
    angles = [
        {"id": "反差感", "desc": "外表看着低调市井，入口完全超乎预期，极具反差冲击。"},
        {"id": "城市性格", "desc": f"一种美食如何折射出{food_profile['city']}清晨或深夜的人间烟火与城市性格。"},
        {"id": "感官细节", "desc": "聚焦滚烫、焦脆、爆汁或爽滑的一瞬间感官生理刺激。"},
        {"id": "地方规矩", "desc": f"为什么{food_profile['city']}当地老饕一定会坚持这样的吃法仪式感。"},
        {"id": "第一口真实体验", "desc": "剥离网红滤镜，还原普通食客第一口最直观的咀嚼味觉解构。"}
    ]
    return random.choice(angles)

def generate_hooks(food_profile: dict, char: dict) -> list:
    """Stage 3: 动态生成 5 个强 Hook 候选 (8-16字，短促有力，一个视觉事件+一句话)"""
    food = food_profile["canonical_name"]
    city = food_profile["city"]
    
    candidates = [
        f"{city}人的清晨，下手比谁都狠。",
        f"等一下，这里面的汤汁有点犯规。",
        f"敢在老居民楼下排长队的，全是硬角色。",
        f"别眨眼，这一铲子下去才是灵魂所在。",
        f"闻着想走，吃完一口直接不想走。"
    ]
    if "热干面" in food:
        candidates = [
            "武汉人的早晨，真有点狠。",
            "三十秒拌不开，这一碗就废了。",
            "在武汉过早，千万别跟面客客气气。",
            "这勺芝麻酱，比我想象得要厚得多。",
            "敢把早餐吃得这么雷厉风行的，只有武汉。"
        ]
    elif "生煎" in food:
        candidates = [
            "等等，这一个里面全是滚烫高汤？",
            "这一锅开盖，整个弄堂全醒了。",
            "吃生煎敢大口咬的，都是狠人。",
            "底有多脆，里面的肉汁就有多凶。",
            "老上海人的下午茶，原来这么热气腾腾。"
        ]
    elif "烧烤" in food:
        candidates = [
            "大口吃肉，才是成年人最纯粹的快乐。",
            "别眨眼，这一抽铁签有多痛快？",
            "在淄博吃烧烤，桌上没有炉子就别坐下。",
            "小葱一折面饼一裹，这口谁顶得住？",
            "淄博的夜市，藏着最滚烫的人间烟火。"
        ]
    return candidates

def generate_natural_narration(food_profile: dict, char: dict, hook: str) -> dict:
    """Stage 4: 自然真实中文旁白生成 (严格 120-155 字，1-2 个 Punchline，去 AI 腔)"""
    food = food_profile["canonical_name"]
    city = food_profile["city"]
    ingredients = food_profile["core_ingredients"]
    
    if "热干面" in food:
        segments = {
            "shot1": hook, # ~12字
            "shot2": f"随便一家老店，灶台腾着大团白汽，食客端着纸碗站在路边开拌。", # 28字
            "shot3": f"大笊篱沸水里一沉一浮，面捞起扣入碗，一勺稠厚纯芝麻酱立马盖上。", # 29字
            "shot4": f"撒上辣萝卜丁，双手翻挑三十秒挂满浓酱，面条偏硬筋道。", # 25字
            "shot5": f"大口下肚，坚果浓香醇厚，萝卜丁的脆特别解腻，越嚼越香。", # 26字
            "shot6": f"武汉人的早晨，靠这一口把自己彻底叫醒。" # 20字 (Punchline)
        }
    elif "生煎" in food:
        segments = {
            "shot1": hook, # ~14字
            "shot2": f"老弄堂拐角的小铺，排队的人全盯着大铁锅，谁也不急。", # 24字
            "shot3": f"木锅盖一掀，水汽混着油香轰地散开，撒满葱花芝麻。", # 23字
            "shot4": f"铲起焦黄脆底，咬开一个小口，清亮高汤慢慢淌出。", # 22字
            "shot5": f"先抿一口鲜汤，肉馅紧实弹牙，香醋正好解了酥脆的油气。", # 25字
            "shot6": f"弄堂里这一口热烫，胜过太多华而不实的东西。" # 21字 (Punchline)
        }
    else: # 淄博烧烤与通用
        segments = {
            "shot1": hook, # ~14字
            "shot2": f"露天排档通红的独立小炭炉，才是老饕碰头的专属暗号。", # 25字
            "shot3": f"五花肉在炭火上滋啦冒油，微小火星窜起，焦香扑鼻。", # 23字
            "shot4": f"折面饼刷面酱，压上一根嫩葱，反手一抽，焦脆肉块全留饼里。", # 27字
            "shot5": f"小葱清脆辛香，撞开五花肉爆出的肉汁，越嚼越过瘾。", # 24字
            "shot6": f"围炉大口吃肉，人间烟火气，大概就是这个模样。" # 22字 (Punchline)
        }

    total_chars = sum(len(txt) for txt in segments.values())
    return {
        "segments": segments,
        "total_chars": total_chars
    }

def build_v2_storyboard(food_profile: dict, char: dict, hook: str, narration_data: dict) -> list:
    """Stage 5: 动态 6 镜分镜架构规划与提示词构建"""
    char_name = char.get("name", "女主")
    food = food_profile["canonical_name"]
    city = food_profile["city"]
    segs = narration_data["segments"]
    master_photo = char.get("photo_path", "assets/character_master/shen_zhao_master.jpg")

    # 统一 6 镜叙事架构 (6~8秒/镜)
    shots = [
        {
            "id": 1,
            "start": 0.0,
            "end": 4.0,
            "duration": 4.0,
            "function": "hook",
            "title": "动态黄金抓人钩子 (视觉事件+情绪反应)",
            "focus": "character+food",
            "reference_strategy": "character_reference",
            "initial_image": master_photo,
            "action": f"女主{char_name}手持刚出锅冒着热气的{food}准备品尝，眼神聚焦食物带有一丝好奇与期待，微推镜头",
            "narration": segs["shot1"],
            "dialogue": segs["shot1"],
            "prompt": f"电影级中近景平缓微推镜头。严格保持与人物参考图完全相同的中国女性：保持相同面部身份、五官、发型、妆容、服装和饰品，不改变服装和饰品。画面主体为20岁中国女性{char_name}，优雅手持刚制作出锅、冒着细腻半透明白色蒸汽的{food}对准镜头，动作自然生动，眼神明亮专注，自然流露微讶与期待的自然微表情。暖黄色市井氛围光，35mm电影镜头浅景深，皮肤纹理真实自然，极致食物质感与生活呼吸感。"
        },
        {
            "id": 2,
            "start": 4.0,
            "end": 10.0,
            "duration": 6.0,
            "function": "context",
            "title": "城市环境与市井烟火交代",
            "focus": "character+scene",
            "reference_strategy": "previous_frame",
            "action": f"女主{char_name}从容坐在{city}市井餐馆木桌前，身姿舒展挺拔，周围食客笑谈，店内环境烟火氤氲",
            "narration": segs["shot2"],
            "dialogue": segs["shot2"],
            "prompt": f"电影级中景平缓横移镜头。严格保持与人物参考图完全相同的中国女性：保持相同面部身份、五官、发型、妆容、服装和饰品。20岁中国女性{char_name}自然端坐在{city}老字号市井餐馆的木桌旁，神态放松自信，身姿挺拔修长。背景是食客谈笑与后厨升腾的白色热气，暖色调自然光影，环境层次真实细腻，电影胶片质感。"
        },
        {
            "id": 3,
            "start": 10.0,
            "end": 18.0,
            "duration": 8.0,
            "function": "signature_process",
            "title": "最具辨识度的制作高潮过程",
            "focus": "food_process",
            "reference_strategy": "food_reference",
            "action": f"后厨操作台特写：{food_profile['signature_process'][0]}，热气升腾，酱汁淋入瞬间微沸",
            "narration": segs["shot3"],
            "dialogue": segs["shot3"],
            "prompt": f"电影级特写俯角微下潜跟焦镜头。聚焦{city}{food}最经典的制作过程：刚离火的滚烫食材在大铁锅或灶台之间剧烈翻动，大团细腻半透明的浓郁白汽升腾弥漫，秘制酱汁与金黄油脂在食材表面折射出诱人光泽，真实食材重力与流动感，4K超高清细节与电影级光影。"
        },
        {
            "id": 4,
            "start": 18.0,
            "end": 27.0,
            "duration": 9.0,
            "function": "food_detail",
            "title": "特色吃法细节与地道秘密",
            "focus": "food_detail",
            "reference_strategy": "previous_frame",
            "action": f"近景特写：筷子熟练操作{food_profile['signature_eating_method'][0]}，层次分明，油润光泽",
            "narration": segs["shot4"],
            "dialogue": segs["shot4"],
            "prompt": f"电影级慢动作微距前移镜头。镜头聚焦于{food}的局部细节与层次结构：纤细自然的手部握着餐具熟练展示正统地道吃法，酱汁浓稠挂壁，配菜色泽新鲜分明，真实细腻的微观物理动态，光泽通透，浅景深虚化背景。"
        },
        {
            "id": 5,
            "start": 27.0,
            "end": 37.0,
            "duration": 10.0,
            "function": "taste",
            "title": "女主真正品尝与自然微表情反差",
            "focus": "character+taste",
            "reference_strategy": "reanchor_character",
            "action": f"女主{char_name}将刚弄好的{food}送入口中轻嚼品味，微顿半秒，眉头轻舒露出一抹真实的惊喜与满足微笑",
            "narration": segs["shot5"],
            "dialogue": segs["shot5"],
            "prompt": f"电影级中近景面部特写平缓微推镜头。严格保持与人物参考图完全相同的中国女性：保持相同面部身份、五官、发型、妆容、服装和饰品。女主{char_name}将美食送入口中细细咀嚼，动作自然优雅，真实面部肌肉动态。入口瞬间眼神停顿半秒，随后自然浮现眉梢轻扬的惊喜赞叹与满足微笑，真实微表情，拒绝夸张网红大瞪眼，极具真实感官说服力。"
        },
        {
            "id": 6,
            "start": 37.0,
            "end": 45.0,
            "duration": 8.0,
            "function": "verdict",
            "title": "从容总结与城市记忆金句收尾",
            "focus": "character+verdict",
            "reference_strategy": "previous_frame",
            "action": f"女主{char_name}咽下食物，直视镜头露出坦荡从容的浅笑，眼神灵动有态度，自然收尾",
            "narration": segs["shot6"],
            "dialogue": segs["shot6"],
            "prompt": f"电影级中近景固定机位镜头。严格保持与人物参考图完全相同的中国女性：保持相同面部身份、五官、发型、妆容、服装和饰品。女主{char_name}满足品尝后从容看向镜头，眼神带有一丝老饕专有的通透与温和笑意，神情自信，光影温暖柔和，为全片带来充满记忆点的从容收尾，真人实拍电影质感。"
        }
    ]
    return shots

def create_v2_project(food_name: str, city: str = "", character_query: str = None, output_path: str = None):
    """主工厂入口：生成完整的 V2 项目工程配置"""
    pool = load_character_pool()
    char = select_character(pool, character_query, food_name, city)
    food_profile = conduct_food_research(food_name, city=city or char.get("city", ""))
    angle = plan_creative_angle(food_profile)
    hooks = generate_hooks(food_profile, char)
    selected_hook = hooks[0] # 默认选第1个最强hook
    
    narration_data = generate_natural_narration(food_profile, char, selected_hook)
    storyboard = build_v2_storyboard(food_profile, char, selected_hook, narration_data)
    
    project_id = f"{food_name.replace(' ', '_')}_v2_45s"
    
    config = {
        "project_id": project_id,
        "title": f"{food_profile['city']}{food_name}",
        "food_title": food_profile["canonical_name"],
        "city": food_profile["city"],
        "character": {
            "character_id": char.get("character_id", "shen_zhao_yujie"),
            "女主姓名": char.get("name", "女主"),
            "风格定位": char.get("style_label", "特色风"),
            "定妆原图路径": char.get("photo_path", "assets/character_master/shen_zhao_master.jpg"),
            "身材与面貌特征": char.get("visual_traits", ""),
            "personality": char.get("personality", ""),
            "voice_persona": char.get("voice_persona", {})
        },
        "character_reference": char.get("photo_path", "assets/character_master/shen_zhao_master.jpg"),
        "food_profile": food_profile,
        "creative_angle": angle,
        "hooks": hooks,
        "selected_hook": selected_hook,
        "narration": {
            "total_chars": narration_data["total_chars"],
            "segments": narration_data["segments"]
        },
        "storyboard": {
            "total_shots": len(storyboard),
            "target_duration": 45.0,
            "aspect_ratio": "9:16",
            "shots": storyboard
        },
        "shots": storyboard
    }

    if not output_path:
        out_dir = os.path.join(WORKSPACE_ROOT, "examples")
        os.makedirs(out_dir, exist_ok=True)
        output_path = os.path.join(out_dir, f"{project_id}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"✨ [V2 全案生成成功] 已生成《{config['food_title']}》45秒动态工程配置！")
    print(f"📁 配置文件: {output_path}")
    print(f"👸 选定女主: {config['character']['女主姓名']} ({config['character']['风格定位']})")
    print(f"🎯 核心角度: {angle['id']} - {angle['desc']}")
    print(f"🪝 黄金钩子: {selected_hook}")
    print(f"📝 旁白字数: {narration_data['total_chars']} 字 (标准区间: 120-155字)")
    print(f"🎬 分镜数量: {len(storyboard)} 镜 (推荐 6 镜动态叙事)")
    return config, output_path

def main():
    parser = argparse.ArgumentParser(description="中华美食短视频全案生成脚手架 (V2 动态工业版)")
    parser.add_argument("--food", type=str, required=True, help="美食名称，如: 武汉热干面、上海生煎、淄博烧烤")
    parser.add_argument("--city", type=str, default="", help="归属城市，如: 武汉、上海、淄博")
    parser.add_argument("--character", type=str, default=None, help="指定女主姓名或风格标签，如: 沈昭、姜黎、御姐、港风")
    parser.add_argument("--out", type=str, default=None, help="自定义输出 JSON 路径")
    args = parser.parse_args()

    create_v2_project(args.food, city=args.city, character_query=args.character, output_path=args.out)

if __name__ == "__main__":
    main()
