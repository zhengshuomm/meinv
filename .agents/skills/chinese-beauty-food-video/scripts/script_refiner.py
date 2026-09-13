#!/usr/bin/env python3
"""
中华美食短视频剧本台词生成与去 AI 腔打磨工具 (V2 动态工业版)
核心规范：
1. 动态 6 镜自然叙事旁白，总字数严格控制在 120～155 个汉字；
2. 全篇最多只允许 1～2 个爆点金句 (Punchline)，其余全部为真实具体、接地气的味觉与火候解构；
3. 严格过滤 AI 油腻词汇（禁止“天灵盖”、“治好了所有内耗”、“直接把我吃沉默了”、“这不是XX是XX”等）；
4. 支持生成专供大模型深度打磨的提示词并联动 Chrome 执行。
"""

import os
import sys
import json
import re
import subprocess
import argparse

FORBIDDEN_AI_PHRASES = [
    "老饕",
    "老饕黑话",
    "老饕专属",
    "治好了所有内耗",
    "直撞天灵盖",
    "直冲天灵盖",
    "舌头彻底缴械",
    "直接起义",
    "舌头投降",
    "直接把我吃沉默了",
    "这不是",
    "这是凶",
    "绝绝子",
    "香迷糊",
    "封神",
    "按头安利",
    "沦陷",
    "上头"
]

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
            "style_label": "冷艳懂吃御姐风",
            "personality": "高冷飒爽、懂行挑剔、极度自信、对美食毫不妥协。",
            "expression_style": "言简意赅、观察细腻、点出关键火候与本味。"
        }
    if character_query:
        for char in pool:
            if character_query in char.get("name", "") or character_query == char.get("character_id", "") or character_query in char.get("style_label", ""):
                return char
    if food_name:
        for char in pool:
            for match in char.get("best_match_cuisines", []):
                if match in food_name or food_name in match:
                    return char
    return pool[0]

def generate_v2_draft_script(food_name: str, char: dict, city: str = "") -> list:
    """生成符合 V2 6 镜规范的初版自然台词 (总字数 125~145 字)"""
    char_name = char.get("name", "女主")
    city_name = city or "本地"

    shots = [
        {"shot_id": 1, "stage": "Hook 抓人钩子 (女主直视镜头亲口说)", "range": "0-4s", "target_len": "8-16字", "text": f"在{city_name}吃美食，不讲究这个吃法就白来了！"},
        {"shot_id": 2, "stage": "Context 环境交代 (女主面对镜头自然介绍)", "range": "4-10s", "target_len": "20-28字", "text": f"带大家来这家本地老店，灶台热气腾腾，坐满了老街坊！"},
        {"shot_id": 3, "stage": "Process 制作高潮 (女主指着后厨介绍)", "range": "10-18s", "target_len": "25-30字", "text": f"看师傅这熟练手艺，猛火翻滚热气升腾，香气扑鼻太霸道了！"},
        {"shot_id": 4, "stage": "Secret 吃法与质感细节 (女主亲手展示吃法)", "range": "18-27s", "target_len": "22-28字", "text": f"吃它一定要趁热，搭配当地秘制调料，层次一下就绝了！"},
        {"shot_id": 5, "stage": "Taste 真实品尝体验 (女主咀嚼后对镜头点评)", "range": "27-37s", "target_len": "24-30字", "text": f"入口外酥里嫩，地道鲜香在舌尖彻底化开，真的太惊艳了！"},
        {"shot_id": 6, "stage": "Verdict 记忆金句收尾 (女主直视镜头从容收尾)", "range": "37-45s", "target_len": "18-24字", "text": f"这一口滚烫好味道，藏着{city_name}最真诚的人间烟火！"}
    ]
    return shots

def validate_script(shots: list) -> dict:
    """校验脚本是否符合 V2 规范与去 AI 腔要求"""
    issues = []
    total_chars = 0
    forbidden_found = []

    for s in shots:
        txt = s.get("text", "")
        clean_len = len(re.sub(r'[,.!?，。！？\s]', '', txt))
        total_chars += clean_len
        for fb in FORBIDDEN_AI_PHRASES:
            if fb in txt:
                forbidden_found.append((s["shot_id"], fb))

    if total_chars < 120:
        issues.append(f"总字数偏少 ({total_chars}字)，建议控制在 120～155 字。")
    elif total_chars > 160:
        issues.append(f"总字数偏多 ({total_chars}字)，45秒内语速过赶，建议精简至 155 字内。")

    if forbidden_found:
        fb_desc = ", ".join([f"第{sid}镜包含'{fb}'" for sid, fb in forbidden_found])
        issues.append(f"检测到 AI 油腻词汇: {fb_desc}")

    return {
        "valid": len(issues) == 0,
        "total_chars": total_chars,
        "issues": issues
    }

def format_refinement_prompt(food_name: str, char: dict, draft_shots: list, city: str = "") -> str:
    """生成专供大模型 (DeepSeek / ChatGPT) 深度打磨的 V2 提示词"""
    char_name = char.get("name", "女主")
    style_label = char.get("style_label", "特色风")
    
    lines_text = "\n".join([f"第{s['shot_id']}镜 ({s['stage']}, {s['range']})：{s['text']} (当前{len(re.sub(r'[,.!?，。！？ ]', '', s['text']))}字)" for s in draft_shots])
    
    prompt = f"""你是一名深谙中国民间饮食哲学与市井烟火风骨的顶级美食短视频文学编剧。
请对以下【中国美女品鉴中华美食短视频】的 6 镜旁白台词进行自然生活化润色打磨。

【品鉴美食】：{city}{food_name}
【出镜女主】：{char_name}（{style_label}）

【初版 6 镜台词】：
{lines_text}

【V2 工业打磨红线】：
1. 【总字数严格限制】：全片 6 镜总字数严格控制在 120～150 个汉字之间，语速自然从容，绝不高频赶场；
2. 【全篇只许 1～2 个金句】：绝大多数句子必须是普通食客的具体味觉描述（如“面是偏硬的”、“酱很稠但不会盖住面香”、“最后萝卜丁那一下脆特别关键”）；
3. 【坚决剔除 AI 油腻腔】：严禁出现“直撞天灵盖”、“治好了所有内耗”、“舌头彻底缴械”、“这不是XX是XX”、“直接把我吃沉默了”等塑料词汇；
4. 【单向递进叙事】：Shot1钩子 ➔ Shot2环境 ➔ Shot3制作 ➔ Shot4特色细节 ➔ Shot5真实咀嚼 ➔ Shot6从容收尾；
5. 【纯中文 JSON 输出格式】：
```json
[
  {{"shot_id": 1, "text": "精炼台词..."}},
  {{"shot_id": 2, "text": "精炼台词..."}},
  {{"shot_id": 3, "text": "精炼台词..."}},
  {{"shot_id": 4, "text": "精炼台词..."}},
  {{"shot_id": 5, "text": "精炼台词..."}},
  {{"shot_id": 6, "text": "精炼台词..."}}
]
```
"""
    return prompt

def main():
    parser = argparse.ArgumentParser(description="中华美食短视频台词打磨与去 AI 腔工具 (V2 动态版)")
    parser.add_argument("--food", type=str, required=True, help="美食名称")
    parser.add_argument("--city", type=str, default="", help="城市")
    parser.add_argument("--character", type=str, default=None, help="女主姓名或风格")
    parser.add_argument("--prompt", action="store_true", help="打印大模型打磨提示词")
    args = parser.parse_args()

    pool = load_character_pool()
    char = select_character(pool, args.character, args.food)
    draft_shots = generate_v2_draft_script(args.food, char, args.city)
    
    validation = validate_script(draft_shots)

    print(f"🥢 《{args.city}{args.food}》V2 动态 6 镜旁白初稿 (女主: {char.get('name', '女主')}):")
    for s in draft_shots:
        print(f"  [{s['shot_id']}] {s['stage']} ({s['range']}): {s['text']} ({len(s['text'])}字)")
    print(f"\n📊 总字数: {validation['total_chars']} 字 | 合规状态: {'✅完全合规' if validation['valid'] else '⚠️存在建议'}")
    if validation["issues"]:
        for issue in validation["issues"]:
            print(f"  - {issue}")

    if args.prompt:
        prompt_str = format_refinement_prompt(args.food, char, draft_shots, args.city)
        print("\n" + "="*50)
        print("📝 大模型 (DeepSeek/ChatGPT) 深度打磨提示词：")
        print("="*50)
        print(prompt_str)

if __name__ == "__main__":
    main()
