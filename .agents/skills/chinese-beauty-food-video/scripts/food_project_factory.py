#!/usr/bin/env python3
"""
中华美食短视频工程立项脚手架 (纯中文版)
功能：
1. 从永久女主库中智能匹配或随机挑选一位女主，全片8镜从头到尾锁定该女主；
2. 固定绑定该女主独有的性格、说话音色与表达口吻；
3. 选配抖音热门爆款中文BGM与闪避混音策略；
4. 100% 生成纯中文六段式视频生成提示词与严苛负向约束。
"""

import os
import sys
import json
import random
import argparse

def load_character_pool():
    pool_path = os.path.join(os.path.dirname(__file__), "..", "references", "character_roster_pool.json")
    if os.path.exists(pool_path):
        with open(pool_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("characters", [])
    return []

def select_character(pool, character_query=None, food_name=None):
    if not pool:
        return {
            "character_id": "shen_zhao_yujie",
            "name": "沈昭",
            "style_label": "高冷老饕御姐风",
            "visual_traits": "20岁，冷白皮，身材高挑172cm超模比例，修长大长腿，精致下颌线，微挑猫眼，右眼角下方带有一颗标志性微小精致泪痣，高扎利落黑马尾，身穿黑色高开叉修身针织裙配黑色皮靴，银色蛇骨锁骨链，清冷高级伪素颜妆容。",
            "personality": "高冷飒爽、懂行挑剔、极度自信、对美食毫不妥协，反差萌极强。",
            "voice_persona": {"voice_name": "zh-CN-XiaoxiaoNeural", "style": "cheerful", "rate": "+10%"},
            "expression_style": "毒舌犀利、一针见血、老饕黑话张口就来。"
        }
    
    # 1. 精确指定 ID 或姓名
    if character_query:
        for char in pool:
            if character_query in char.get("name", "") or character_query == char.get("character_id", "") or character_query in char.get("style_label", ""):
                return char
                
    # 2. 根据美食智能契合推荐
    if food_name:
        for char in pool:
            for match in char.get("best_match_cuisines", []):
                if match in food_name or food_name in match:
                    return char
                    
    # 3. 随机选配一位
    return random.choice(pool)

BGM_DATABASE = {
    "高冷老饕御姐风": {"track": "《市井小调》（欢快古风琵琶卡点纯音乐）", "genre": "市井古风卡点", "energy": "节奏明快、提神带劲"},
    "清纯初恋邻家风": {"track": "《想去海边》（原声吉他轻快跳跃版）", "genre": "温暖治愈民谣", "energy": "甜美轻快、清新治愈"},
    "新中式国风古典风": {"track": "《青花瓷》（清雅纯筝典雅纯音）", "genre": "东方丝竹古韵", "energy": "优雅悠扬、如诗如画"},
    "90年代港风复古明艳风": {"track": "《初恋》（复古微醺慢摇萨克斯版）", "genre": "港岛复古慢摇", "energy": "慵懒微醺、高级从容"},
    "知性书卷温婉风": {"track": "《江南雨碎》（温润丝竹琵琶纯音）", "genre": "温润东方电台", "energy": "娓娓道来、抚慰人心"},
    "灵动猫系千金名媛风": {"track": "《欢喜就好》（国风欢快轻音乐伴奏）", "genre": "俏皮轻快国潮", "energy": "娇憨灵动、充满喜感"},
    "川渝江湖元气小辣椒": {"track": "《人间烟火》（国风轻快竹笛节奏版）", "genre": "热辣市井烟火", "energy": "欢快热烈、食欲大开"},
    "阳光街头酷飒辣妹风": {"track": "《吹灭小山河》（欢快竹笛伴奏版）", "genre": "街头江湖侠气", "energy": "痛快爽朗、豪迈大气"},
    "森系日杂清透氧气风": {"track": "《起风了》（温暖木吉他空灵指弹版）", "genre": "治愈空灵木吉他", "energy": "温柔纯净、静谧温润"},
    "赛博国潮机能拽姐风": {"track": "《囍》（重低音唢呐国潮电音卡点版）", "genre": "国潮电音重低音", "energy": "炸裂狠辣、专治不服"},
    "夜色微醺纯欲辣妹风": {"track": "《风的季节》（慢调爵士铜管纯音乐）", "genre": "微醺爵士慢调", "energy": "夜色撩人、高级奢华"},
    "奢雅黑裙名媛御姐风": {"track": "《风的季节》（慢调复古微醺纯音乐）", "genre": "微醺爵士慢调", "energy": "奢雅从容、高级质感"},
    "都市轻熟明朗探店风": {"track": "《吹灭小山河》（轻快竹笛伴奏版）", "genre": "明快市井轻音乐", "energy": "活力明快、亲切生动"},
    "极简纯欲私享名媛风": {"track": "《起风了》（温暖木吉他空灵指弹版）", "genre": "空灵治愈纯音乐", "energy": "松弛轻柔、高级私享"}
}

def load_custom_script(script_path: str) -> list:
    """加载经过大模型打磨后的完美剧本台词"""
    if not os.path.exists(script_path):
        return None
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    # 尝试解析 JSON
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return [item.get("台词") or item.get("text") or str(item) for item in data]
        if isinstance(data, dict):
            lines = data.get("润色后分镜台词") or data.get("shots") or data.get("台词") or []
            if lines:
                return [item.get("台词") or item.get("text") or str(item) for item in lines]
    except Exception:
        pass
    # 按行解析
    lines = [line.strip() for line in content.split("\n") if line.strip() and not line.startswith("#")]
    return lines

def create_food_project(food_name: str, character_query: str = None, region_hint: str = "川渝", custom_script_path: str = None):
    pool = load_character_pool()
    char = select_character(pool, character_query, food_name)
    char_name = char.get("name", "女主")
    style_label = char.get("style_label", "特色风")
    bgm_info = BGM_DATABASE.get(style_label, {"track": "《人间烟火》（国风轻快竹笛版）", "genre": "市井轻音乐", "energy": "欢快舒畅"})
    
    project_id = f"{food_name.replace(' ', '_')}_45秒全案"
    
    config = {
        "项目编号": project_id,
        "美食主题": food_name,
        "归属地域": region_hint,
        "出镜女主设定": {
            "女主姓名": char_name,
            "风格定位": style_label,
            "定妆原图路径": char.get("photo_path", ""),
            "身材与面貌特征": char.get("visual_traits", ""),
            "固定性格": char.get("personality", ""),
            "固定说话音色": char.get("voice_persona", {}),
            "固定表达口癖": char.get("expression_style", "")
        },
        "抖音爆款背景音乐配置": {
            "推荐中文曲目": bgm_info["track"],
            "音乐风格": bgm_info["genre"],
            "情绪调性": bgm_info["energy"],
            "智能闪避混音策略": "人声口播时音量压低至18%垫乐，第一口咀嚼试吃时BGM瞬间静音留白突出清脆ASMR拟音，前3秒钩子与收尾金句重音卡点强化完播。"
        },
        "视频总时长": 45.0,
        "画面比例": "竖屏 9:16",
        "母带标准电平": "-17.0 LUFS 广播级标准",
        "分镜列表": [
            {
                "镜号": 1,
                "时间": "0.0秒 - 3.0秒",
                "时长": 3.0,
                "阶段定位": "黄金3秒反常识钩子 (感官核爆)",
                "景别与运镜": "电影级超微距极慢平稳前推镜头",
                "画面描述": f"刚出锅滚烫翻滚的{food_name}在铁锅中剧烈滋啦冒泡，大团细腻半透明的白色蒸汽扑面而来，金黄酥脆或红亮诱人，油脂折射出极其诱人的高光。",
                "参考帧继承策略": "食物微距基准首帧",
                "旁白台词": "看着最不起眼的小摊，下手往往最狠。",
                "字数": 17,
                "声音拟音与音乐控制": "重音顿音伴随热油爆裂滋啦声；BGM卡点切入 (30%音量)",
                "纯中文视频生成提示词": f"电影级超微距极慢平稳前推镜头。刚出锅滚烫翻滚的{food_name}正在剧烈滋啦翻滚冒泡，浓郁诱人的油花飞溅，大团细腻半透明的热腾腾白色热气升腾扑面而来，暖黄色钨丝灯光在食材表面折射出通透金红高光，浅景深虚化背景。真人电影实拍质感，4K超高清细腻质感，24帧自然动态模糊，极致食欲冲击。"
            },
            {
                "镜号": 2,
                "时间": "3.0秒 - 8.0秒",
                "时长": 5.0,
                "阶段定位": "建立背景与女主入场 (立人设与气场)",
                "景别与运镜": "电影级中景水平推进镜头，展现挺拔身材与修长大长腿",
                "画面描述": f"锁定的女主{char_name}优雅端坐在市井老字号小店木桌前，展现出{char.get('visual_traits', '')}，眼神自信从容，嘴角带着老饕专属浅笑，静待美食端上。",
                "参考帧继承策略": f"绑定女主定妆原图 ({char.get('photo_path', '')})",
                "旁白台词": f"在本地敢把招牌做成这副模样的，全是有恃无恐的狠角色。",
                "字数": 26,
                "声音拟音与音乐控制": "市井人声鼎沸环境音；BGM音量平滑压低至18%作为垫乐",
                "纯中文视频生成提示词": f"电影级中景水平平缓推进镜头。画面主体为锁定的20岁中国美女{char_name}，{char.get('visual_traits', '')}，神情从容自信，身段挺拔，优雅端坐在市井烟火气老字号餐馆木桌前，长腿线条自然优美舒展。店内暖黄灯光与远处白色水汽交织，真实皮肤毛孔与发丝细节，4K真人实拍电影感。"
            },
            {
                "镜号": 3,
                "时间": "8.0秒 - 14.0秒",
                "时长": 6.0,
                "阶段定位": "微观烹饪与烟火镬气 (火候密码)",
                "景别与运镜": "快速平移下潜特写镜头，聚焦灶台火候",
                "画面描述": f"老师傅手起勺落，猛火颠锅翻炒{food_name}，浓烈白烟带着火星升腾而起，秘制酱汁瞬间爆香，镬气十足。",
                "参考帧继承策略": "继承第2镜环境，特写后厨操作台",
                "旁白台词": f"差一秒火候就老，多一滴料汁就腻，老饕的心全被这勺镬气拿捏了。",
                "字数": 28,
                "声音拟音与音乐控制": "猛火轰鸣声、大铁锅铿锵翻炒撞击声；BGM平稳烘托",
                "纯中文视频生成提示词": f"特写快速俯角推进镜头。后厨猛火灶台上火舌翻滚，老师傅动作极其利落地快速颠勺爆炒{food_name}，浓郁的白色蒸汽夹杂着热油焦香猛烈升腾，酱汁淋入铁锅的一瞬间剧烈爆裂，市井烟火镬气十足，真实微观动态，4K高清电影光影。"
            },
            {
                "镜号": 4,
                "时间": "14.0秒 - 20.0秒",
                "时长": 6.0,
                "阶段定位": "沉浸互动与老饕规矩 (专业吃法仪式感)",
                "景别与运镜": "特写镜头微俯拍伴随轻微跟焦",
                "画面描述": f"女主{char_name}纤纤玉手拿起筷子或调羹，动作内行地拌匀或蘸取特制料汁，神情专注且享受。",
                "参考帧继承策略": "继承第2镜女主手部与身形",
                "旁白台词": f"吃它得懂规矩，趁着滚烫十秒内翻拌均匀，让每一处都挂满滋味。",
                "字数": 27,
                "声音拟音与音乐控制": "餐具轻碰瓷碗声、浓稠酱汁翻拌声；BGM低缓流动",
                "纯中文视频生成提示词": f"特写镜头轻微跟焦。锁定的女主{char_name}纤细优美的手指握着深色竹筷，动作极其熟练优雅地将刚出锅的{food_name}充分翻拌裹匀酱汁，食材裹满红亮光泽，热气徐徐升起，真实手部肌理与瓷碗温润质感，浅景深电影画面。"
            },
            {
                "镜号": 5,
                "时间": "20.0秒 - 26.0秒",
                "时长": 6.0,
                "阶段定位": "极致食欲特写近景 (食欲巅峰瞬间)",
                "景别与运镜": "电影级极慢动作微距滑移镜头",
                "画面描述": f"筷子挑起挂满酱汁的{food_name}举至镜头前，晶莹剔透，浓醇酱汁顺着边缘欲滴未滴，高光闪烁。",
                "参考帧继承策略": "继承第4镜食材特写",
                "旁白台词": "这香味不是飘出来的，是直接撞进天灵盖的霸道。",
                "字数": 22,
                "声音拟音与音乐控制": "浓汁滴落微音、细微滋啦沸腾音；BGM逐渐弱化",
                "纯中文视频生成提示词": f"电影级慢动作微距推进镜头。筷子夹起一块诱人饱满的{food_name}，浓稠诱人的酱汁如琥珀般挂在边缘缓缓滴落，表层油脂在暖黄灯光下折射出璀璨高光，热气微动，4K超写实极致食欲细节。"
            },
            {
                "镜号": 6,
                "时间": "26.0秒 - 33.0秒",
                "时长": 7.0,
                "阶段定位": "第一口试吃高潮与反转 (情绪释放)",
                "景别与运镜": "中近景面部特写平缓微推镜头，精准捕捉微表情",
                "画面描述": f"女主{char_name}将食物送入口中轻咬咀嚼，冷傲/平静的神情瞬间融化，双眸因极致美味猛然放大，惊喜满足地陶醉颔首。",
                "参考帧继承策略": f"【强制重定向】回溯至第2镜女主{char_name}面部末帧，绝不继承第5镜无脸食材",
                "旁白台词": "第一口还没咽下去，舌头先缴械投降，胃跟着直接起义了。",
                "字数": 25,
                "声音拟音与音乐控制": "【BGM瞬间留白静音】；极清脆咬碎咔嚓脆响或大口吸溜吞咽声",
                "纯中文视频生成提示词": f"【重定向锚定第2镜女主定妆末帧】中近景面部特写平缓微推镜头。锁定的20岁中国女主{char_name}将美食送入口中轻咬，真实自然的咀嚼动作，入口瞬间眼神从从容转化为难以置信的惊喜放大，眉梢舒展，嘴角泛起彻底沉沦的陶醉浅笑与赞叹颔首，真实面部毛孔纹理与咀嚼吞咽微动态，4K超清电影画质。"
            },
            {
                "镜号": 7,
                "时间": "33.0秒 - 39.0秒",
                "时长": 6.0,
                "阶段定位": "老饕深度品味与灵魂升华",
                "景别与运镜": "中景镜头平缓后拉，融于市井暖光",
                "画面描述": f"女主{char_name}满足地放下筷子，轻舒一口气，眼神深情而通透，整个人被温暖晨光与香气笼罩。",
                "参考帧继承策略": "继承第6镜试吃末帧，锁死面容体态",
                "旁白台词": "有些城市靠风景让人记住，有些城市，全凭这一口不讲理的霸道。",
                "字数": 28,
                "声音拟音与音乐控制": "碗筷轻轻落桌声；BGM主旋律重新升起推向高潮",
                "纯中文视频生成提示词": f"中景平缓慢移镜头。锁定的女主{char_name}轻轻放下筷子，面容带着极致满足的惬意浅笑，双目柔和深情，阳光与店内暖黄灯光在侧脸镀上一层金色光晕，周围食客笑语欢声，市井生活纪实电影感。"
            },
            {
                "镜号": 8,
                "时间": "39.0秒 - 45.0秒",
                "时长": 6.0,
                "阶段定位": "直视镜头对口型金句与评论区收尾",
                "景别与运镜": "固定机位中近景平视对镜头直视",
                "画面描述": f"女主{char_name}直接抬眸直视镜头，展现迷人自信眼神杀，口型严密对齐最后一句金句，话毕微扬下巴从容一笑，慢淡出。",
                "参考帧继承策略": "继承第7镜末帧，精准对口型",
                "旁白台词": "本地老饕在评论区集合，这家到底正不正宗？你敢来挑战吗？",
                "字数": 26,
                "声音拟音与音乐控制": "BGM重音落定收束，随画面慢慢优雅淡出",
                "纯中文视频生成提示词": f"固定机位中近景直视镜头。锁定的女主{char_name}直接抬起明澈自信的双眸注视着摄像机镜头，嘴唇自然开合清晰说出收尾金句台词，面部表情灵动迷人，口型自然饱满完全对齐，语毕嘴角勾起一抹从容飒爽的浅笑，伴随画面平滑优雅慢淡出，4K电影画质。"
            }
        ],
        "严苛负向约束": "严禁换脸、严禁变脸、严禁突变不同人、严禁塑料假脸、严禁过度磨皮失真、严禁动漫卡通画风、严禁假吃假嚼、严禁面无表情、严禁畸形手指、严禁多余四肢、严禁肢体变异、严禁西方人面孔、严禁夸张网红大浓妆、严禁低俗不雅姿势、严禁画面突然卡顿跳切、严禁画面闪烁撕裂、严禁画面模糊低分辨率、严禁背景突变。",
        "爆款封面推荐": [
            f"本地人打死不说的{food_name}！",
            f"第一口直接把我吃沉默了",
            f"长得最不起眼，下手最狠！"
        ],
        "爆款标题推荐": [
            f"在本地吃{food_name}千万别说微辣！第一口直接把我吃沉默了",
            f"别跟我提米其林！导航会骗你，但这家开了几十年的老店绝不会！",
            f"舌头先投降胃跟着起义！美女老饕带你吃透真正的{food_name}灵魂",
            f"看着最不起眼的小摊，下手往往最狠！这口滋味谁顶得住？",
            f"如果你只能选一道菜代表家乡，它能不能排进前三？"
        ],
        "评论区互动引爆设计": f"本地老饕在评论区集合：这家店的{food_name}到底算几星水平？交出你们心里真正的私藏王牌据点！"
    }
    
    # 如果提供了打磨后的完美剧本，则替换各分镜台词并重新计算字数
    if custom_script_path:
        custom_lines = load_custom_script(custom_script_path)
        if custom_lines and len(custom_lines) >= 8:
            print(f"✨ 正在注入大模型打磨后的完美剧本台词 ({len(custom_lines)} 句)...")
            import re
            for i in range(8):
                new_text = custom_lines[i]
                config["分镜列表"][i]["旁白台词"] = new_text
                config["分镜列表"][i]["字数"] = len(re.sub(r'[，。！？、“”《》\s]', '', new_text))
    
    return config

def main():
    parser = argparse.ArgumentParser(description="生成 45 秒中华美食短视频工程配置 (纯中文版)")
    parser.add_argument("--food", type=str, required=True, help="美食名称，如 '重庆火锅'")
    parser.add_argument("--character", type=str, default=None, help="指定女主姓名或ID，如 '沈昭'、'林初薇'、'苏婉清'，留空则智能契合或随机")
    parser.add_argument("--region", type=str, default="川渝", help="美食地域，如 '川渝'、'广东'、'西北'、'江浙'、'东北'")
    parser.add_argument("--script-file", type=str, default=None, help="传入经 OpenAI/DeepSeek 打磨后的完美剧本台词文件路径")
    parser.add_argument("--output", type=str, default=None, help="输出 JSON 配置文件路径")
    
    args = parser.parse_args()
    config = create_food_project(args.food, args.character, args.region, args.script_file)
    
    out_path = args.output
    if not out_path:
        out_path = f"{args.food.replace(' ', '_')}_45秒全案.json"
    
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 成功生成 100% 纯中文短视频工程配置: {out_path}")
    print(f"🍜 美食主题: {config['美食主题']} ({config['归属地域']})")
    print(f"👑 出镜女主: {config['出镜女主设定']['女主姓名']} ({config['出镜女主设定']['风格定位']}) [全片8镜严格锁定，绝不换脸]")
    print(f"🎵 抖音中文BGM: {config['抖音爆款背景音乐配置']['推荐中文曲目']}")

if __name__ == "__main__":
    main()
