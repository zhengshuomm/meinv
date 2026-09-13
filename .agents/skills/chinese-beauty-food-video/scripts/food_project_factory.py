#!/usr/bin/env python3
"""
中华美食短视频工程立项脚手架 (V3 全英文提示词 + 女主亲口对镜头说中文台词 + 通用架构版)
执行链路：
Food Research (事实校验) 
  ➔ Creative Angle (核心创意角度) 
  ➔ Hook Generator (动态黄金钩子，8-16字，女主直视镜头亲口说) 
  ➔ First-Person Host Dialogue (出镜女主第一人称大白话台词，120-155字，严禁装腔AI词) 
  ➔ Universal Storyboard Planner (动态 6 镜叙事架构) 
  ➔ 100% English Cinematic Prompt Builder (全英文分镜提示词 + 口型动作控制 + 英文负向排斥)
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
            "style_label": "冷艳懂吃御姐风",
            "photo_path": "assets/character_master/shen_zhao_master.jpg",
            "visual_traits": "20岁，冷白皮，身材高挑172cm超模比例，修长身材，清冷高级下颌线，微挑猫眼，右眼角小泪痣，黑色高马尾，身穿黑色修身V领针织长裙配银色细锁骨链。",
            "hair_face_anchor_en": "20-year-old Chinese beauty Shen Zhao, fair porcelain skin, sharp elegant jawline, slight cat-eye makeup, distinct tiny delicate beauty mark below right eye, high sleek neat black ponytail",
            "wardrobe_anchor_en": "wearing an iconic black tight-fitting knit midi dress with side slit, silver snake-bone clavicle necklace, black leather ankle boots",
            "speaking_style_en": "looking directly into the lens, actively speaking in Chinese with confident, sharp mouth articulation and assertive, captivating eye contact",
            "negative_prompt_en": "no outfit change, no hairstyle change, no loose hair, no different clothes, no western face, no distorted hands, no blurry, no low quality, no morphing",
            "voice_persona": {"voice_name": "zh-CN-XiaoxiaoNeural", "style": "cheerful", "rate": "+10%"}
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
    """Stage 1: 地方美食事实调研 (构建 food_profile，支持任意菜品通用生成)"""
    known_database = {
        "热干面": {
            "canonical_name": "武汉热干面",
            "city": "武汉",
            "city_en": "Wuhan",
            "food_en": "Wuhan hot dry noodles (Reganmian)",
            "province": "湖北",
            "category": "特色面食 / 过早文化",
            "core_ingredients": ["碱水面（提前掸过放凉）", "纯芝麻酱（小磨香油化开）", "辣萝卜丁", "酸豆角", "香葱", "生抽老抽", "少许蒜水"],
            "signature_process": ["沸水锅中大笊篱捞面几秒即起", "扣入纸碗甩净水分", "大勺淋上稠厚香浓的纯芝麻酱", "飞快撒入红亮辣萝卜丁与葱花"],
            "signature_process_en": "a chef lifts a large bamboo strainer filled with yellow alkaline noodles from boiling cauldrons, transferring into a bowl and pouring a thick, velvety ladle of deep golden-brown pure sesame sauce cascading over noodles",
            "signature_eating_method": ["必须在30秒内用筷子上下飞速翻拌均匀", "让每一根粗面条均匀挂满浓酱", "趁热大口挑起吃"],
            "signature_eating_method_en": "wooden chopsticks rapidly toss and fold the firm noodles, coating every single strand with rich, viscous aromatic sesame paste and crunchy red pickled radish cubes",
            "visual_highlights": ["捞面瞬间升腾的浓白水汽", "深褐色芝麻酱如绸缎般浇在黄色碱面上", "双手筷子翻飞快速拌匀的动感", "爽脆红萝卜丁"],
            "texture": ["面条扎实筋道微偏硬", "芝麻酱醇厚粘稠浓郁", "萝卜丁清脆解腻"],
            "flavor": ["浓郁复合芝麻坚果香", "咸鲜微辣微甜", "后味麦香回甘"],
            "cultural_context": "武汉人清晨‘过早’的精神图腾，边走边吃，雷厉风行。",
            "common_misconceptions": ["误以为是煮烂的挂面", "误以为放麻酱很多水会稀", "放陈醋或者花生酱（外地改版）"],
            "must_not_show": ["清汤面条", "面条软烂断裂", "优雅用刀叉吃", "长时间放置坨成面饼"]
        },
                "生腌": {
            "canonical_name": "潮汕生腌（海鲜毒药）",
            "city": "潮汕",
            "city_en": "Chaoshan",
            "food_en": "Chaoshan raw marinated seafood",
            "province": "广东",
            "category": "生鲜风味 / 潮汕夜市",
            "core_ingredients": ["鲜活红膏青蟹", "深海基围虾", "新鲜生蚝", "高浓度纯粮白酒", "优质生抽", "大量大蒜碎", "鲜朝天椒碎", "香菜与少许冰糖"],
            "signature_process": ["活蟹洗净斩块，露出如红宝石般饱满半透明的诱人红膏", "淋入用生抽、蒜米、鲜辣椒粒与白酒调配的秘制生腌料汁", "置于碎冰上冰镇腌制入味，膏体晶莹剔透如天然果冻"],
            "signature_process_en": "master chef freshly carving live mud crabs to reveal glistening crimson roe, generously pouring chilled aromatic marinade infused with soy sauce, minced garlic, bird eye chilies and rice wine over ice",
            "signature_eating_method": ["用小勺或直接吸吮，轻轻抿一口如果冻般细腻绵密的冰凉鲜甜蟹膏，鲜香蒜辣瞬间在舌尖化开"],
            "signature_eating_method_en": "gently savoring the melt-in-mouth jelly-like raw crab roe, chilled sweet seafood essence bursting with fiery garlic and herbal cilantro notes",
            "visual_highlights": ["碎冰盘上红白分明、如果冻般晶莹剔透的生腌膏蟹", "鲜亮酱汁与青翠芫荽蒜末的点缀", "轻轻一挤虾肉如果冻般滑出"],
            "texture": ["蟹膏如冰淇淋果冻般绵密细腻", "虾肉鲜甜脆弹紧致", "冰凉滑糯透光"],
            "flavor": ["极致本味鲜甜", "浓郁蒜香微辣", "纯正酒香回甘微醺"],
            "cultural_context": "被誉为‘潮汕毒药’，吃过一次就让人欲罢不能的深夜至鲜。",
            "common_misconceptions": ["以为是下铁锅炒熟的", "用死蟹制作", "放很多油去炸"],
            "must_not_show": ["大铁锅热油翻炒", "滚烫水汽扑面", "熟海鲜颜色变白变干", "油炸冒烟"]
        },
        "牛肉面": {
            "canonical_name": "兰州牛肉面",
            "city": "兰州",
            "city_en": "Lanzhou",
            "food_en": "Lanzhou hand-pulled beef noodles",
            "province": "甘肃",
            "category": "传统面食 / 西北经典",
            "core_ingredients": ["手工现拉优质拉面", "大锅慢熬清亮牛肉牛骨浓汤", "白萝卜薄片", "红亮熟油泼辣子", "新鲜香菜与青蒜苗末", "现切大片卤牛肉"],
            "signature_process": ["拉面师傅双手飞快甩拉分条，面条如丝落入滚沸大锅几秒即熟", "长筷捞起甩净水分入粗瓷大碗", "大勺舀起滚烫清亮牛肉原汤浇入，大勺泼入红亮油泼辣子并撒满青绿蒜苗"],
            "signature_process_en": "noodle master gracefully stretching and slamming dough into delicate strands, dropping into boiling water and scooping into ceramic bowls, topped with clear aromatic beef broth and brilliant red chili oil",
            "signature_eating_method": ["先喝一口鲜亮微辣的牛肉原汤，再双手用长筷把红油与蒜苗快速挑拌散开，大口吸溜筋道有嚼劲的面条"],
            "signature_eating_method_en": "sipping a spoonful of rich spiced broth first, then tossing firm elastic noodles with chili oil and fragrant garlic sprouts, slurping heartily",
            "visual_highlights": ["拉面师傅双手飞扬甩面的张力", "红亮辣子浮在清澈骨汤上的鲜明对撞", "大团升腾的麦香与骨汤白汽", "大口吸溜面条的痛快"],
            "texture": ["面条韧劲十足爽滑弹牙", "牛肉酥烂入味", "萝卜薄软透光"],
            "flavor": ["一清二白三红四绿五黄", "汤清肉烂", "辣油香浓而不燥"],
            "cultural_context": "兰州人一天的精神支柱，讲究‘一清二白三红四绿五黄’。",
            "common_misconceptions": ["叫兰州拉面（当地人只叫牛肉面）", "用铁锅炒面", "汤色浑浊发黑"],
            "must_not_show": ["机器挂面", "铁锅爆炒", "放很多酱油炒成黑褐色"]
        },
        "螺蛳粉": {
            "canonical_name": "柳州螺蛳粉",
            "city": "柳州",
            "city_en": "Liuzhou",
            "food_en": "Liuzhou spicy river snail rice noodles",
            "province": "广西",
            "category": "地方小吃 / 酸辣名品",
            "core_ingredients": ["陈米发酵干米粉", "鲜活石螺与筒骨慢熬浓汤", "酸笋", "炸至金黄酥脆大片腐竹", "酸豆角与木耳丝", "炸花生米", "特制红油"],
            "signature_process": ["滚水锅中汆烫爽滑米粉捞入大碗", "码上大片金黄蜂窝炸腐竹、酸笋与酸豆角", "大勺舀起滚烫鲜红香浓的螺蛳原汤浇在米粉上，红油透亮扑鼻"],
            "signature_process_en": "scalding silky rice noodles in boiling water, topping with giant crispy golden tofu skin sheets, tangy pickled bamboo shoots, and ladling fiery red spicy snail broth",
            "signature_eating_method": ["先把金黄炸腐竹按进红油螺蛳汤里吸饱鲜辣汤汁，大口嗦入爽滑Q弹的米粉，酸笋的脆爽与汤底的鲜辣在嘴里瞬间爆开"],
            "signature_eating_method_en": "pressing the crunchy tofu skin deep into the pungent broth to soak up juices, then enthusiastically slurping bouncy rice noodles with crispy pickled bamboo",
            "visual_highlights": ["巨大金黄蜂窝炸腐竹浸入红汤的吸汁过程", "鲜红透亮的螺蛳红油与碧绿青菜", "筷子挑起爽滑米粉大口嗦粉"],
            "texture": ["米粉爽滑Q弹有韧劲", "腐竹外吸汁内酥香", "酸笋爽脆酸爽"],
            "flavor": ["酸、辣、鲜、爽、烫", "独特的发酵酸笋香与螺肉浓鲜"],
            "cultural_context": "柳州最具辨识度的市井名片，闻着臭吃着香的极致反差。",
            "common_misconceptions": ["以为里面有大颗螺蛳肉", "用面条代替米粉", "不放酸笋"],
            "must_not_show": ["面条面粉质感", "干拌无汤", "没有炸腐竹和酸笋"]
        },
        "生煎": {
            "canonical_name": "上海生煎包",
            "city": "上海",
            "city_en": "Shanghai",
            "food_en": "Shanghai pan-fried soup dumplings (Shengjianbao)",
            "province": "上海",
            "category": "传统点心",
            "core_ingredients": ["半发酵面皮", "紧实猪肉馅（加入皮冻熬制高汤）", "香葱", "黑白芝麻", "菜籽油"],
            "signature_process": ["大平底生铁锅密密麻麻排满生煎", "油煎到底部微黄后泼水加盖焖熟", "揭开巨大木质锅盖瞬间水汽轰然腾起", "撒上大把碧绿葱花与炒香芝麻"],
            "signature_process_en": "a massive wooden lid is lifted from a giant cast-iron skillet, unleashing dense billows of savory steam and sizzling oil crackles, generously showered with emerald green scallions and toasted sesame seeds",
            "signature_eating_method": ["先开窗后喝汤，轻轻咬开侧面上方小口，吹凉后先吸鲜甜肉汁，再蘸镇江香醋吃皮肉与焦底"],
            "signature_eating_method_en": "delicately nibbling a small opening on the side, gently sipping the piping-hot glistening amber meat broth before dipping the crispy golden bottom crust into dark vinegar",
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
            "city_en": "Zibo",
            "food_en": "Zibo charcoal barbecue with flatbread and scallions",
            "province": "山东",
            "category": "市井烧烤",
            "core_ingredients": ["散发麦香的山东手工薄面饼", "临淄嫩青白小葱", "秘制咸鲜甜面酱", "现切炭烤五花肉与牛肉串"],
            "signature_process": ["师傅先在大火炉烤至七八成熟", "端上桌放在每桌专属双层红泥独立小炭炉上翻烤", "肉串滋啦冒出金色油花"],
            "signature_process_en": "pork belly and beef skewers sizzling intensely over a personal double-tiered red-clay charcoal brazier, fat rendering and dripping onto glowing embers with crackling micro-sparks",
            "signature_eating_method": ["左手拿薄面饼对折沾上甜面酱，夹上一整根嫩小葱，包裹刚离火的滚烫肉串，右手利落反手反抽铁签，整口吞嚼"],
            "signature_eating_method_en": "folding a warm thin flatbread brushed with sweet bean sauce, wrapping around a crisp green scallion stalk and sizzling meat skewers, then deftly pulling out the metal skewers in one slick backward pull",
            "visual_highlights": ["红泥独立炭炉红炭火星微爆", "面饼裹肉利落反手抽铁签的爽快瞬间", "小葱青翠与焦黄五花肉的色彩反差"],
            "texture": ["面饼麦香韧劲", "五花肉焦香外脆内爆油", "生小葱清甜脆嫩解腻"],
            "flavor": ["炭火焦香", "酱香甜咸", "葱香微辛带甘"],
            "cultural_context": "山东齐鲁大地的豪爽烟火气，围炉而坐的真诚与纯粹。",
            "common_misconceptions": ["直接撸串不卷饼", "用大葱而不是细嫩小葱", "不放甜面酱"],
            "must_not_show": ["电烤箱", "普通冷冻速冻肉串", "没有独立小烤炉"]
        },
        "烤鸭": {
            "canonical_name": "北京烤鸭",
            "city": "北京",
            "city_en": "Beijing",
            "food_en": "Beijing roast duck (Peking duck)",
            "province": "北京",
            "category": "宫廷名菜 / 传统美食",
            "core_ingredients": ["果木挂炉现烤填鸭", "手工荷叶饼", "特制甜面酱", "清脆葱丝与黄瓜条"],
            "signature_process": ["果木挂炉烤至鸭皮枣红发亮", "师傅推车现场片鸭，刀法飞快", "鸭皮酥脆冒油，肉质细嫩带汁"],
            "signature_process_en": "a master chef carving a whole glossy amber-roasted duck with razor-sharp knife movements, crisp translucent skin crackling delicately and juicy tender breast meat sliced in graceful motions",
            "signature_eating_method": ["取温热荷叶饼抹甜面酱，码上鸭皮与鸭肉，放葱丝黄瓜条，折叠卷起，整卷入口"],
            "signature_eating_method_en": "layering crisp duck skin and tender meat onto a thin lotus leaf pancake with sweet bean sauce, adding fresh scallion shreds and cucumber, folding into a neat roll",
            "visual_highlights": ["枣红油亮透光的鸭皮切片", "现场片鸭飞快刀工", "薄如蝉翼的荷叶饼包裹"],
            "texture": ["鸭皮酥脆香浓", "鸭肉鲜嫩多汁", "黄瓜葱丝爽脆解腻"],
            "flavor": ["果木炭火清香", "鸭脂甘香甜美", "面酱咸甜浓郁"],
            "cultural_context": "京城百年非遗名菜，刀工与火候的极致讲究。",
            "common_misconceptions": ["整只手撕吃", "皮软不脆"],
            "must_not_show": ["冷冻烤鸭加热", "皮肉分离软烂"]
        },
        "麻婆豆腐": {
            "canonical_name": "成都麻婆豆腐",
            "city": "成都",
            "city_en": "Chengdu",
            "food_en": "Chengdu Mapo Tofu with minced beef and Sichuan peppercorn",
            "province": "四川",
            "category": "川味名菜 / 江湖菜",
            "core_ingredients": ["细嫩石膏豆腐", "酥脆牛肉末（牛肉臊子）", "郫县豆瓣酱", "汉源大红袍花椒面", "青蒜段"],
            "signature_process": ["大火热铁锅爆香牛肉酥", "豆瓣豆豉煸出红亮辣油", "豆腐下锅推入高汤微火煨透", "三次勾芡收汁撒满花椒面与青蒜"],
            "signature_process_en": "a searing wok churning tender silken tofu cubes in radiant red chili oil with crispy minced beef, bubbling violently with volcanic steam, finished with three rounds of starch slurry and a snowfall of freshly ground Sichuan peppercorn powder",
            "signature_eating_method": ["用瓷勺连汤带豆腐轻舀一勺，吹微凉送入口中，配大碗白米饭，享受麻辣鲜香烫酥嫩"],
            "signature_eating_method_en": "spooning a steaming porcelain scoop of glossy red tofu onto steaming white rice, the silken tofu melting effortlessly on the tongue with tingling numbing spice",
            "visual_highlights": ["红油滚烫密集冒泡", "豆腐白嫩与红油青蒜的色彩对撞", "瓷勺舀起时的晃动嫩滑感"],
            "texture": ["豆腐滑嫩滚烫", "牛肉臊子香酥脆硬", "芡汁浓稠滑亮"],
            "flavor": ["麻、辣、烫、鲜、酥、嫩、整、香（川菜八字真诀）"],
            "cultural_context": "川菜灵魂名片，市井小店里的大师傅功力。",
            "common_misconceptions": ["豆腐碎成渣", "没有花椒的麻味", "用猪肉代替牛肉"],
            "must_not_show": ["白汤豆腐", "冷凉凝固的芡汁"]
        }
    }

    matched = None
    for k, v in known_database.items():
        if k in food_name or food_name in k:
            matched = v.copy()
            break

    if not matched:
        # 通用美食画像动态构建
        matched = {
            "canonical_name": f"{city or ''}{food_name}",
            "city": city or "地方名城",
            "city_en": city or "China",
            "food_en": f"authentic {food_name}",
            "province": province or "地方",
            "category": "地道地方特色美食",
            "core_ingredients": [f"地道现做{food_name}核心主料", "秘制地域风味酱料", "新鲜当地佐料小菜"],
            "signature_process": [f"大锅热气翻滚现做{food_name}", "师傅熟练操作出锅瞬间热气氤氲", "趁热装盘淋上特调料汁"],
            "signature_process_en": f"artisan chef skilfully cooking fresh {food_name} in intense heat, thick fragrant steam billowing with sizzling culinary energy and glossy appetizing colors",
            "signature_eating_method": [f"趁刚出锅最热腾腾时品尝第一口，搭配当地特制蘸料"],
            "signature_eating_method_en": f"enjoying piping hot {food_name} at its freshest peak, dipping into authentic regional condiments to highlight rich textures and savory depths",
            "visual_highlights": [f"刚出锅升腾的白色热气", f"{food_name}金黄诱人的纹理与油润光泽", "用筷子夹起或盛起的细节特写"],
            "texture": ["外脆内嫩或筋道爽滑", "层次丰富鲜美"],
            "flavor": ["地道鲜香浓郁", "地道本味回甘"],
            "cultural_context": f"{city or '当地'}市井烟火深处代代相传的地道滋味。",
            "common_misconceptions": ["误以为是工业预制菜", "非当地正统搭配吃法"],
            "must_not_show": ["冷冰冰无热气", "机器流水线质感", "违背当地正统吃法的手法"]
        }
    return matched

def plan_creative_angle(food_profile: dict, tone_preference: str = None) -> dict:
    """Stage 2: 创意角度决策"""
    angles = [
        {"id": "反差感", "desc": "外表看着低调市井，入口完全超乎预期，极具反差冲击。"},
        {"id": "城市性格", "desc": f"一种美食如何折射出{food_profile['city']}清晨或深夜的人间烟火与城市性格。"},
        {"id": "感官细节", "desc": "聚焦滚烫、焦脆、爆汁或爽滑的一瞬间感官生理刺激。"},
        {"id": "地方讲究", "desc": f"为什么{food_profile['city']}本地人总坚持这种地道吃法讲究。"},
        {"id": "第一口真实体验", "desc": "剥离网红滤镜，还原普通食客第一口最直观的咀嚼味觉解构。"}
    ]
    return random.choice(angles)

def generate_hooks(food_profile: dict, char: dict) -> list:
    """Stage 3: 动态生成 5 个强 Hook 候选 (女主直视镜头亲口说，短促有力，8-16字)"""
    food = food_profile["canonical_name"]
    city = food_profile["city"]
    
    if "热干面" in food:
        candidates = [
            "三十秒拌不开，这一碗面直接作废！",
            "在武汉过早，你可千万别跟面客气！",
            "这勺浓稠芝麻酱，比我想象的厚太多了！",
            "敢把早餐吃得这么雷厉风行的，只有武汉！",
            "等一下！谁说热干面吃起来会干喉咙？"
        ]
    elif "生腌" in food:
        candidates = [
            "等一下！这口潮汕生腌到底有多让人上瘾？",
            "敢在潮汕深夜吃这口冰淇淋蟹膏的，都是狠角色！",
            "别眨眼！这晶莹如果冻的红膏，谁看谁迷糊！",
            "第一口是微凉鲜甜，第二口彻底回不去了！",
            "被称作海鲜毒药的潮汕生腌，终于被我吃到了！"
        ]
    elif "牛肉面" in food or "拉面" in food:
        candidates = [
            "等一下！在兰州吃牛肉面，你可千万别叫拉面！",
            "师傅这一甩一拉，几十秒下锅才叫真功夫！",
            "别眨眼！这一大勺红亮辣油泼下去才是灵魂！",
            "一清二白三红四绿，这口热汤能治愈所有疲惫！",
            "清晨这一碗扎实的肉烂汤鲜，彻底叫醒一整座城！"
        ]
    elif "螺蛳粉" in food:
        candidates = [
            "等一下！谁说柳州螺蛳粉只有臭没有香？",
            "别眨眼！这一大片蜂窝炸腐竹吸饱红汤有多绝？",
            "敢在柳州大口嗦粉加特辣的，全是真英雄！",
            "酸笋清脆米粉弹牙，这一口酸辣滚烫太过瘾了！",
            "闻着退后三步，吃完第一口直接不想走了！"
        ]
    elif "生煎" in food:
        candidates = [
            "等一下！吃生煎敢大口咬的，全是狠人！",
            "这一锅刚揭盖，整条弄堂全被香醒了！",
            "别眨眼！这一个生煎里面全是滚烫高汤！",
            "底有多酥脆，里面的肉汁就有多滚烫！",
            "老上海人的下午茶，原来这么热气腾腾！"
        ]
    elif "烧烤" in food:
        candidates = [
            "在淄博吃烧烤，桌上没有独立小炉子千万别坐下！",
            "别眨眼！这一反手抽铁签到底有多痛快？",
            "大口吃肉，才是成年人最纯粹的快乐！",
            "嫩小葱一折面饼一裹，这口谁顶得住？",
            "淄博的夜市，藏着最滚烫的人间烟火！"
        ]
    elif "烤鸭" in food:
        candidates = [
            "等一下！吃北京烤鸭最惊艳的居然不是鸭肉？",
            "果木炭火烤出这一身枣红，香气太霸道了！",
            "别眨眼！看师傅这一刀下去有多酥脆！",
            "荷叶饼一卷甜面酱一抹，这口地道京味绝了！",
            "百年老北京的讲究，全藏在这口脆皮里！"
        ]
    elif "麻婆豆腐" in food:
        candidates = [
            "等一下！这勺滚烫红油豆腐有点太犯规了！",
            "敢在成都大口咽麻婆豆腐的，都是勇士！",
            "别眨眼！这一把汉源花椒面撒下去才是灵魂！",
            "不用嚼直接化开，这口麻辣鲜香太下饭了！",
            "最市井的川味，藏着最极致的火候讲究！"
        ]
    else:
        candidates = [
            f"在{city}吃{food}，如果不讲究这个吃法就白来了！",
            f"敢在老居民楼下排长队的，绝对全是硬角色！",
            f"别眨眼！这一锅刚出炉的香气太霸道了！",
            f"等一下！这第一口的味道完全超出我预期！",
            f"这口传承了几十年的老味道，谁尝谁知道！"
        ]
    return candidates

def generate_first_person_dialogue(food_profile: dict, char: dict, hook: str) -> dict:
    """
    Stage 4: 女主面对镜头亲口说的第一人称地道中文口语大白话台词
    - 绝非第三人称画外音旁白，而是出镜女主亲口对观众说！
    - 严格 120-155 字，1-2 个 Punchline，杜绝装腔，拒绝“老饕”等生僻AI词。
    """
    food = food_profile["canonical_name"]
    city = food_profile["city"]
    
    if "热干面" in food:
        segments = {
            "shot1": hook, # ~16字 (女主直视镜头张口说)
            "shot2": f"带你们钻武汉老巷子，灶台冒着白汽，全是地道老街坊！", # 25字
            "shot3": f"大笊篱在滚水里几秒捞起，大勺浓稠芝麻酱盖得太扎实了！", # 26字
            "shot4": f"双手飞快翻挑三十秒，必须让每根面条都裹满厚酱！", # 24字
            "shot5": f"面条筋道偏硬，醇厚坚果香混着辣萝卜丁，太过瘾了！", # 24字
            "shot6": f"吃完这碗热干面，才算真正融进了武汉的早晨！" # 22字
        }
    elif "生腌" in food:
        segments = {
            "shot1": hook, # ~18字
            "shot2": f"带你们来潮汕深夜排档，碎冰铺满档口，全是鲜活海鲜！", # 24字
            "shot3": f"鲜活红膏青蟹现斩现腌，淋上秘制蒜蓉辣酱，如果冻般晶莹！", # 26字
            "shot4": f"不用任何加热，直接用小勺挖起冰镇红膏，鲜甜冰凉！", # 23字
            "shot5": f"入口像冰淇淋一样绵密，海鲜本味鲜甜混着蒜辣，太绝了！", # 25字
            "shot6": f"这口潮汕海鲜毒药，吃过一次就彻底印在灵魂里！" # 22字
        }
    elif "牛肉面" in food or "拉面" in food:
        segments = {
            "shot1": hook, # ~19字
            "shot2": f"带你们来兰州头锅老店，大锅热气升腾，坐满本地食客！", # 24字
            "shot3": f"看师傅双手飞甩下锅捞起，浇入滚烫清亮牛肉原汤与辣油！", # 25字
            "shot4": f"先趁热喝一口原汤，再用筷子把辣油拌匀，大口吸溜！", # 23字
            "shot5": f"面条爽滑有嚼劲，浓汤混着油辣子，一口下去整个人都暖了！", # 26字
            "shot6": f"一清二白三红四绿，这碗面就是兰州最真诚的清晨！" # 23字
        }
    elif "螺蛳粉" in food:
        segments = {
            "shot1": hook, # ~18字
            "shot2": f"带你们钻进柳州老巷，老店锅炉滚沸，满街都是霸道浓香！", # 24字
            "shot3": f"爽滑米粉汆烫出锅，码上大片蜂窝炸腐竹，浇入鲜红螺蛳原汤！", # 26字
            "shot4": f"先把炸腐竹按进红油吸饱鲜辣汤汁，再夹起酸笋大口嗦粉！", # 24字
            "shot5": f"米粉爽滑弹牙，酸笋清脆酸爽，红油鲜辣在舌尖爆开，太过瘾了！", # 28字
            "shot6": f"闻着退后三步，吃完不想走，柳州这口酸辣谁能抗拒！" # 23字
        }
    elif "生煎" in food:
        segments = {
            "shot1": hook, # ~17字
            "shot2": f"带你们来排弄堂老店，一锅刚出炉，整条街都被香醒了！", # 25字
            "shot3": f"大木盖一掀热气轰地散开，师傅大把撒上葱花芝麻，太香了！", # 27字
            "shot4": f"先开窗后喝汤，轻轻咬个小口，先把清甜滚烫肉汁吸干净！", # 27字
            "shot5": f"底壳焦脆爆汁，肉馅弹牙多汁，蘸点香醋完全不腻，绝配！", # 26字
            "shot6": f"弄堂里这一口滚烫鲜香，才是老上海最踏实的烟火气！" # 24字
        }
    elif "烧烤" in food:
        segments = {
            "shot1": hook, # ~19字
            "shot2": f"带你们来本地老排档，一进门炭火飘香，每桌都热气腾腾！", # 26字
            "shot3": f"五花肉在炭火上滋啦冒油，小火星直窜，焦香扑鼻太霸道了！", # 27字
            "shot4": f"薄饼抹上面酱，压上嫩葱反手一抽铁签，焦脆肉块全留饼里！", # 27字
            "shot5": f"小葱清甜脆嫩，刚好解了五花肉爆出的热油，越嚼越过瘾！", # 26字
            "shot6": f"大口卷饼大口吃肉，淄博这股滚烫烟火气，真的太绝了！" # 25字
        }
    elif "烤鸭" in food:
        segments = {
            "shot1": hook, # ~17字
            "shot2": f"带你们来品百年挂炉，一进店就是纯正的果木炭火清香！", # 25字
            "shot3": f"看师傅现场飞快片鸭，皮肉相连枣红透亮，油脂滋啦响！", # 25字
            "shot4": f"热荷叶饼抹甜面酱，放上酥脆鸭皮与细嫩鸭肉，码上葱丝卷起！", # 28字
            "shot5": f"鸭皮薄脆酥香，鸭肉鲜嫩多汁，黄瓜葱丝清脆解腻，太绝了！", # 27字
            "shot6": f"传承百年的京城讲究，这一口至味真的人间值得！" # 23字
        }
    elif "麻婆豆腐" in food:
        segments = {
            "shot1": hook, # ~18字
            "shot2": f"钻进成都老街坊，锅铲一响，满屋子全是勾人的麻辣香气！", # 26字
            "shot3": f"铁锅猛火翻滚红油，牛肉臊子酥脆，最后一把花椒面是灵魂！", # 27字
            "shot4": f"连汤带汁舀上一大勺浇在白米饭上，这红亮看着就流口水！", # 26字
            "shot5": f"豆腐嫩滑到在舌尖化开，麻辣鲜香瞬间爆开，太下饭了！", # 25字
            "shot6": f"这一口滚烫鲜麻，藏着成都最地道的江湖滋味！" # 22字
        }
    else:
        segments = {
            "shot1": hook, # ~18字
            "shot2": f"带大家来本地老店，灶台热气腾腾，坐满了街坊！", # 23字
            "shot3": f"看师傅这熟练手艺，猛火翻滚热气升腾，香气扑鼻！", # 24字
            "shot4": f"吃它一定要趁热，搭配当地秘制调料，层次绝了！", # 24字
            "shot5": f"入口外酥里嫩，地道鲜香在舌尖化开，太惊艳了！", # 23字
            "shot6": f"这一口滚烫好味道，藏着{city}最真诚的人间烟火！" # 24字
        }

    total_chars = sum(len(txt) for txt in segments.values())
    return {
        "segments": segments,
        "total_chars": total_chars
    }

def build_v3_storyboard(food_profile: dict, char: dict, hook: str, dialogue_data: dict) -> list:
    """
    Stage 5: 动态 6 镜纯中文分镜架构规划
    - 严格遵循 100% 纯中文电影级六段式提示词公式 (纯中文提示词，严禁英文机位词)；
    - 注入女主纯中文视觉强锁定 (hair_face_anchor_cn, wardrobe_anchor_cn)；
    - 注入女主直视镜头张口说中文的生动口播指令 (speaking_style_cn)；
    - 严苛纯中文负向排斥约束 (negative_prompt_cn)；
    - 出镜女主亲口说的中文大白话台词 (dialogue_cn，严格 120-155 字)。
    """
    char_name = char.get("name", "女主")
    food = food_profile["canonical_name"]
    city = food_profile["city"]
    segs = dialogue_data["segments"]
    master_photo = char.get("photo_path", "assets/character_master/shen_zhao_master.jpg")

    traits = char.get("visual_traits", "")
    face_anchor = (char.get("hair_face_anchor_cn") or f"20岁年轻中国女子，五官容貌与发型严格与定妆参考图保持完全一致").rstrip("。")
    if "20岁中国美女" in face_anchor:
        face_anchor = face_anchor.replace("20岁中国美女", "20岁年轻中国女子")
    if char_name and char_name in face_anchor:
        face_anchor = face_anchor.replace(char_name, "").strip("，, ")
    wardrobe_anchor = (char.get("wardrobe_anchor_cn") or "身穿角色定妆参考图中的固定服装，严禁中途更换衣服").rstrip("。")
    speaking_style = char.get("speaking_style_cn") or "直接抬眸直视摄像机镜头，眼神自信灵动，嘴唇自然饱满开合，清晰说出地道中文台词，口型动作生动真实，面部微表情随说话自然起伏"
    neg_prompt = char.get("negative_prompt_cn") or "严禁更换服装，严禁改变发型，严禁散发，严禁非指定衣物，严禁洋人面孔，严禁畸变手指，严禁多余手指，严禁闭嘴说话，严禁假唱木偶嘴，严禁卡通动漫，严禁模糊低清"

    proc_cn = "，".join(food_profile.get("signature_process", []))
    eating_cn = "，".join(food_profile.get("signature_eating_method", []))

    is_chilled = any(kw in food for kw in ["生腌", "刺身", "鱼生", "冷盘", "凉拌", "冻", "冰"])
    is_noodle_soup = any(kw in food for kw in ["面", "粉", "汤", "火锅", "粥", "抄手", "馄饨"])

    if is_chilled:
        shot1_food_interaction = f"女主在餐桌前轻托着碎冰盘上晶莹剔透、泛着鲜亮油润光泽的{food}面向镜头。{speaking_style}，亲口说出抓人台词。"
        shot1_atmosphere = "碎冰盘上海鲜晶莹诱人，市井暖色温润光影，真实细腻皮肤质感，浅景深虚化背景，4K电影级超高清画质。"
        shot2_scene = f"背景中其他食客愉快交谈，海鲜档口碎冰与新鲜食材陈列丰富。暖色调市井街头光影，丰富的空间层次景深，电影胶片质感。"
        shot3_atmosphere = f"冰盘上碎冰晶莹透亮，酱汁鲜亮油润，大蒜碎与红辣椒粒点缀其间，食材呈现出新鲜饱满的天然微透明胶质光泽。"
        shot4_atmosphere = f"食材表面挂满鲜亮晶莹的秘制生腌酱汁，红膏诱人，肉质如果冻般剔透，层次分明，令人垂涎欲滴。"
        shot1_action = f"女主{char_name}轻托着冰镇新鲜晶莹的{food}直视镜头，眼神灵动自信，亲口说出抓人台词，嘴唇动作自然清晰"
    elif is_noodle_soup:
        shot1_food_interaction = f"女主在餐桌前轻托着刚端上桌、冒着浓白热气与诱人浓香的{food}面向镜头。{speaking_style}，亲口说出抓人台词。"
        shot1_atmosphere = "刚出锅的美食与镜头之间热气袅袅升腾，市井暖色温润光影，真实细腻皮肤质感，浅景深虚化背景，4K电影级超高清画质。"
        shot2_scene = f"背景中其他食客愉快交谈，灶台大锅翻滚升腾起层层白色热气蒸汽。暖色调市井街头光影，丰富的空间层次景深，电影胶片质感。"
        shot3_atmosphere = f"大锅中浓白热气与鲜香氤氲升腾，汤汁红油翻滚沸腾，食材在热力中剧烈律动，在暖色灯光下折射出诱人光泽。"
        shot4_atmosphere = f"面条与食材表面挂满浓郁汤汁与红亮辣油，热气持续缓缓升腾，层次分明，令人垂涎欲滴。"
        shot1_action = f"女主{char_name}在桌前轻托着热气腾腾的{food}直视镜头，眼神灵动自信，亲口说出抓人台词，嘴唇动作自然清晰"
    else:
        shot1_food_interaction = f"女主手持或轻托着刚出锅冒着浓白热气的{food}面向镜头。{speaking_style}，亲口说出抓人台词。"
        shot1_atmosphere = "刚出锅的美食与镜头之间热气袅袅升腾，市井暖色温润光影，真实细腻皮肤质感，浅景深虚化背景，4K电影级超高清画质。"
        shot2_scene = f"背景中其他食客愉快交谈，后厨灶台翻滚升腾起层层白色热气蒸汽。暖色调市井街头光影，丰富的空间层次景深，电影胶片质感。"
        shot3_atmosphere = f"锅中浓白热气与香气氤氲升腾，热油滋啦作响，食材与酱汁在热力中剧烈翻滚，油脂在暖色灯光下折射出诱人光泽。"
        shot4_atmosphere = f"食材表面挂满浓郁酱汁，油润金黄，热气持续缓缓升腾，层次分明，令人垂涎欲滴。"
        shot1_action = f"女主{char_name}手持或托着刚出炉冒热气的{food}直视镜头，眼神灵动自信，亲口说出抓人台词，嘴唇动作自然清晰"

    shot1_prompt = (
        f"中近景平滑向前微推镜头。画面主体人物五官面貌、发型与服装严格100%与角色定妆参考图完全一致：{face_anchor}，{wardrobe_anchor}。"
        f"{shot1_food_interaction}"
        f"{shot1_atmosphere}"
        f"负向约束：{neg_prompt}。"
    )

    shot2_prompt = (
        f"电影感中景，平滑水平横摇慢移。画面主体人物容貌、发型与服装严格100%与参考图完全一致：{face_anchor}，{wardrobe_anchor}。"
        f"女主自然端坐在{city}市井地道餐馆的餐桌前，面对镜头自然从容，{speaking_style}，向观众介绍这家地道馆子。"
        f"{shot2_scene}"
        f"负向约束：{neg_prompt}。"
    )

    shot3_prompt = (
        f"电影级微距特写镜头，微向下俯拍。聚焦{city}{food}最具代表性的地道制作高潮：{proc_cn}。"
        f"{shot3_atmosphere}"
        f"逼真的物理烹饪动态，极致微距细节，4K电影级超高清质感。"
        f"负向约束：严禁人物杂乱大脸，严禁卡通动漫，严禁CG塑料假质感，严禁画面模糊低清。"
    )

    shot4_prompt = (
        f"微距动态跟随特写镜头。聚焦{food}的地道吃法细节与诱人质感：{eating_cn}。"
        f"{shot4_atmosphere}"
        f"超写实微距质感，平滑运镜，浅景深，市井暖色温润光感。"
        f"负向约束：严禁畸变手指，严禁多余手指或肢体，严禁餐具扭曲变形，严禁卡通动漫，严禁模糊低清。"
    )

    if any(kw in food for kw in ["面", "粉", "丝", "面条"]):
        eat_motion = f"女主用筷子挑起刚做好的{food}大口吸溜送入口中，自然真实咀嚼品尝，下颌与面颊肌肉自然律动。"
    elif any(kw in food for kw in ["生腌", "果冻", "膏", "刺身"]):
        eat_motion = f"女主用小巧瓷勺轻舀一块如冰淇淋果冻般晶莹软嫩的{food}送入口中，自然真实咀嚼品尝，下颌与面颊肌肉自然律动。"
    elif any(kw in food for kw in ["豆腐", "布丁", "冻", "汤", "粥"]):
        eat_motion = f"女主用瓷勺轻舀一块鲜嫩如果冻般的{food}送入口中，自然真实咀嚼品尝，下颌与面颊肌肉自然律动。"
    elif any(kw in food for kw in ["烧烤", "串", "烤肉"]):
        eat_motion = f"女主双手拿着卷好或手持的{food}送入口中大口咬下一角，自然真实咀嚼品尝，下颌与面颊肌肉自然律动。"
    else:
        eat_motion = f"女主将刚做好的{food}送入口中，自然真实咀嚼品尝，下颌与面颊肌肉自然律动。"

    shot5_prompt = (
        f"中近景人像肖像镜头。画面主体人物容貌、发型与服装严格100%与参考图完全一致：{face_anchor}，{wardrobe_anchor}。"
        f"{eat_motion}"
        f"在味道爆发的瞬间微顿半秒，眼神瞬间放大，流露出被极致美味惊艳到的真实喜悦与赞许点头。"
        f"随后她直接抬眸直视摄像机镜头，{speaking_style}，真实分享第一口口感点评，神情真诚生动。"
        f"柔和人像轮廓光，真实皮肤纹理与毛孔细节，浅景深。"
        f"负向约束：{neg_prompt}。"
    )

    shot6_prompt = (
        f"电影感中近景固定机位。画面主体人物容貌、发型与服装严格100%与参考图完全一致：{face_anchor}，{wardrobe_anchor}。"
        f"品尝咽下美食后，女主坦荡从容直视摄像机镜头，眼神自信迷人，面带自然灿烂的微笑，{speaking_style}，亲口说出记忆金句台词，语毕从容优雅轻微点头致意。"
        f"温馨温暖的夜市暖光氛围，柔和轮廓金光勾勒发丝与肩膀，电影母带级调色质感。"
        f"负向约束：{neg_prompt}。"
    )

    shots = [
        {
            "id": 1,
            "start": 0.0,
            "end": 4.0,
            "duration": 4.0,
            "function": "hook",
            "title": "动态黄金抓人钩子 (女主直视镜头亲口说台词)",
            "focus": "character+food",
            "reference_strategy": "character_reference",
            "initial_image": master_photo,
            "action": shot1_action,
            "dialogue_cn": segs["shot1"],
            "dialogue": segs["shot1"],
            "narration": segs["shot1"],
            "prompt": shot1_prompt,
            "prompt_cn": shot1_prompt
        },
        {
            "id": 2,
            "start": 4.0,
            "end": 10.0,
            "duration": 6.0,
            "function": "context",
            "title": "城市环境与市井烟火交代 (女主面对镜头介绍)",
            "focus": "character+scene",
            "reference_strategy": "previous_frame",
            "action": f"女主{char_name}坐在{city}市井餐馆桌前，神态从容自信，面对镜头自然口播介绍这家店",
            "dialogue_cn": segs["shot2"],
            "dialogue": segs["shot2"],
            "narration": segs["shot2"],
            "prompt": shot2_prompt,
            "prompt_cn": shot2_prompt
        },
        {
            "id": 3,
            "start": 10.0,
            "end": 18.0,
            "duration": 8.0,
            "function": "signature_process",
            "title": "最具辨识度的制作高潮 (微距制作全景)",
            "focus": "food_process",
            "reference_strategy": "food_reference",
            "action": f"后厨操作台特写：{proc_cn}，热气升腾，食材与酱汁在热力中剧烈沸腾",
            "dialogue_cn": segs["shot3"],
            "dialogue": segs["shot3"],
            "narration": segs["shot3"],
            "prompt": shot3_prompt,
            "prompt_cn": shot3_prompt
        },
        {
            "id": 4,
            "start": 18.0,
            "end": 27.0,
            "duration": 9.0,
            "function": "food_detail",
            "title": "特色吃法细节与地道秘密 (手部与食物细节)",
            "focus": "food_detail",
            "reference_strategy": "previous_frame",
            "action": f"特写镜头：双手熟练操作正统吃法细节，热气升腾，展现食物诱人层次",
            "dialogue_cn": segs["shot4"],
            "dialogue": segs["shot4"],
            "narration": segs["shot4"],
            "prompt": shot4_prompt,
            "prompt_cn": shot4_prompt
        },
        {
            "id": 5,
            "start": 27.0,
            "end": 37.0,
            "duration": 10.0,
            "function": "taste",
            "title": "女主真实品尝与咀嚼后面对镜头点评 (微表情反差+对镜头说话)",
            "focus": "character+taste",
            "reference_strategy": "reanchor_character",
            "action": f"女主{char_name}将食物送入口中自然咀嚼品尝，微顿半秒露出惊喜神情，随即直视镜头亲口说出真实口感点评",
            "dialogue_cn": segs["shot5"],
            "dialogue": segs["shot5"],
            "narration": segs["shot5"],
            "prompt": shot5_prompt,
            "prompt_cn": shot5_prompt
        },
        {
            "id": 6,
            "start": 37.0,
            "end": 45.0,
            "duration": 8.0,
            "function": "verdict",
            "title": "城市记忆从容收尾 (直视镜头亲口说金句台词)",
            "focus": "character+verdict",
            "reference_strategy": "previous_frame",
            "action": f"女主{char_name}咽下美食，坦荡从容直视镜头，亲口说出城市记忆金句台词，自信微笑自然收尾",
            "dialogue_cn": segs["shot6"],
            "dialogue": segs["shot6"],
            "narration": segs["shot6"],
            "prompt": shot6_prompt,
            "prompt_cn": shot6_prompt
        }
    ]
    return shots

def create_v2_project(food_name: str, city: str = "", character_query: str = None, output_path: str = None):
    """主工厂入口：生成完整的 V4 项目工程配置 (100% 纯中文提示词 + 女主亲口说中文台词)"""
    pool = load_character_pool()
    char = select_character(pool, character_query, food_name, city)
    food_profile = conduct_food_research(food_name, city=city or char.get("city", ""))
    angle = plan_creative_angle(food_profile)
    hooks = generate_hooks(food_profile, char)
    selected_hook = hooks[0]
    
    dialogue_data = generate_first_person_dialogue(food_profile, char, selected_hook)
    storyboard = build_v3_storyboard(food_profile, char, selected_hook, dialogue_data)
    
    if output_path:
        project_id = os.path.splitext(os.path.basename(output_path))[0]
    else:
        project_id = f"{food_profile.get('city_en', 'food')}_{food_name}_45s"
    
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
            "hair_face_anchor_cn": char.get("hair_face_anchor_cn", ""),
            "wardrobe_anchor_cn": char.get("wardrobe_anchor_cn", ""),
            "speaking_style_cn": char.get("speaking_style_cn", ""),
            "negative_prompt_cn": char.get("negative_prompt_cn", ""),
            "hair_face_anchor_en": char.get("hair_face_anchor_en", ""),
            "wardrobe_anchor_en": char.get("wardrobe_anchor_en", ""),
            "personality": char.get("personality", ""),
            "voice_persona": char.get("voice_persona", {})
        },
        "character_reference": char.get("photo_path", "assets/character_master/shen_zhao_master.jpg"),
        "food_profile": food_profile,
        "creative_angle": angle,
        "hooks": hooks,
        "selected_hook": selected_hook,
        "dialogue": {
            "speaker": char.get("name", "女主"),
            "style": "第一人称出镜面对镜头亲口说中文大白话",
            "total_chars": dialogue_data["total_chars"],
            "segments": dialogue_data["segments"]
        },
        "narration": {
            "total_chars": dialogue_data["total_chars"],
            "segments": dialogue_data["segments"]
        },
        "storyboard": {
            "total_shots": len(storyboard),
            "target_duration": 45.0,
            "aspect_ratio": "9:16",
            "prompt_language": "100% 纯中文电影级六段式提示词 (严禁英文机位词)",
            "dialogue_language": "100% 地道中文大白话 (出镜女主亲口说台词，严禁装腔AI词)",
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

    print(f"✨ [V4 全案生成成功] 已生成《{config['food_title']}》45秒动态工程配置！")
    print(f"📁 配置文件: {output_path}")
    print(f"👸 选定女主: {config['character']['女主姓名']} ({config['character']['风格定位']})")
    print(f"🎯 核心角度: {angle['id']} - {angle['desc']}")
    print(f"🪝 女主黄金钩子: {selected_hook}")
    print(f"📝 女主台词字数: {dialogue_data['total_chars']} 字 (标准大白话区间: 120-155字)")
    print(f"🎬 分镜提示词: 100% 纯中文电影级提示词 + 亲口说中文口型动作锁定")
    print(f"🔒 人物一致性: 发型/固定服装/负向词纯中文强锁定注入全部出镜分镜")
    return config, output_path

def main():
    parser = argparse.ArgumentParser(description="中华美食短视频全案生成脚手架 (V4 纯中文提示词+女主口播版)")
    parser.add_argument("--food", type=str, required=True, help="美食名称，如: 武汉热干面、上海生煎、淄博烧烤、北京烤鸭、麻婆豆腐")
    parser.add_argument("--city", type=str, default="", help="归属城市，如: 武汉、上海、淄博、北京、成都")
    parser.add_argument("--character", type=str, default=None, help="指定女主姓名或风格标签，如: 沈昭、林初薇、赵子晴、姜黎")
    parser.add_argument("--out", type=str, default=None, help="自定义输出 JSON 路径")
    args = parser.parse_args()

    create_v2_project(args.food, city=args.city, character_query=args.character, output_path=args.out)

if __name__ == "__main__":
    main()
