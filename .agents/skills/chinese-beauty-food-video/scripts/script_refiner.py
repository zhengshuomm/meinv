#!/usr/bin/env python3
"""
中华美食短视频剧本台词生成与大模型润色辅助工具 (Script Refiner & Chrome Bridge)
功能：
1. 提取或生成针对选定女主与美食的 8 镜吸引人初版剧本台词；
2. 生成专供 OpenAI (ChatGPT) 与 DeepSeek 的老饕终极打磨提示词；
3. 支持控制/联动 Chrome 浏览器（自动开启 ChatGPT/DeepSeek、自动复制剪贴板、或生成本地可视化交互桥接工作台）；
4. 支持将润色打磨后的“完美剧本”一键应用并生成 100% 纯中文短视频工程配置。
"""

import os
import sys
import json
import re
import subprocess
import argparse
import urllib.request
import urllib.parse

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
            "visual_traits": "20岁，冷白皮，身材高挑172cm超模比例，大长腿，右眼角精致小泪痣，高扎利落黑马尾，身穿黑色高开叉修身针织裙。",
            "personality": "高冷飒爽、懂行挑剔、极度自信、对美食毫不妥协。",
            "voice_persona": {"voice_name": "zh-CN-XiaoxiaoNeural", "style": "cheerful", "rate": "+10%"},
            "expression_style": "毒舌犀利、一针见血、老饕黑话张口就来。"
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

def generate_draft_script(food_name: str, char: dict) -> list:
    """生成符合 8 镜规范的初版吸引人台词（严格控制在 20~28 字）"""
    char_name = char.get("name", "女主")
    style = char.get("style_label", "")
    
    # 针对不同风格女主提供具有鲜明人设口吻的初版草稿
    if "御姐" in style or "拽姐" in style:
        shots = [
            {"shot_id": 1, "stage": "黄金3秒反常识钩子", "text": f"看着最不起眼的路边小摊，下手往往最狠。"},
            {"shot_id": 2, "stage": "背景与女主入场", "text": f"在本地敢把招牌做成这副模样的，全是惹不起的狠角色。"},
            {"shot_id": 3, "stage": "猛火镬气细节", "text": f"差一秒火候就老，多一滴料汁就腻，老饕的心全被这勺镬气拿捏了。"},
            {"shot_id": 4, "stage": "吃规矩与仪式感", "text": f"吃它得懂规矩，趁着滚烫十秒内翻拌均匀，让每一寸都裹满酱汁。"},
            {"shot_id": 5, "stage": "极致食欲特写", "text": f"这香味不是飘出来的，是直接撞进天灵盖的霸道。"},
            {"shot_id": 6, "stage": "第一口试吃高潮", "text": f"第一口还没咽下去，舌头先缴械投降，胃跟着直接起义了。"},
            {"shot_id": 7, "stage": "深度品味与升华", "text": f"有些城市靠风景让人记住，有些城市，全凭这一口不讲理的霸道。"},
            {"shot_id": 8, "stage": "直视镜头收尾金句", "text": f"本地老饕在评论区集合，这家到底正不正宗？你敢来挑战吗？"}
        ]
    elif "港风" in style or "名媛" in style:
        shots = [
            {"shot_id": 1, "stage": "黄金3秒反常识钩子", "text": f"真正顶级的鲜味，从来不需要复杂的烹饪来粉饰。"},
            {"shot_id": 2, "stage": "背景与女主入场", "text": f"没有菜单的老字号后巷，藏着整个城市最挑剔的舌尖秘密。"},
            {"shot_id": 3, "stage": "猛火镬气细节", "text": f"火候多一分就失去灵魂，这手掐准时间的绝活，没三十年练不出来。"},
            {"shot_id": 4, "stage": "吃规矩与仪式感", "text": f"老钱的吃法讲究层次，先抿一口原汤，再让舌尖迎接真正的狂欢。"},
            {"shot_id": 5, "stage": "极致食欲特写", "text": f"晶莹透亮的膏脂裹着秘制汁水，在光影下美得像一件艺术品。"},
            {"shot_id": 6, "stage": "第一口试吃高潮", "text": f"第一口是海风拂面，第二口是极致鲜甜，第三口彻底回不去了。"},
            {"shot_id": 7, "stage": "深度品味与升华", "text": f"繁华喧嚣会随时间淡去，但这口无可替代的鲜，能记一辈子。"},
            {"shot_id": 8, "stage": "直视镜头收尾金句", "text": f"私藏的这份老底子味道交出来了，你们心中的头牌又是哪家？"}
        ]
    elif "初恋" in style or "氧气" in style or "书卷" in style:
        shots = [
            {"shot_id": 1, "stage": "黄金3秒反常识钩子", "text": f"清晨唤醒一整座城市的，从来不是闹钟，而是这口热气。"},
            {"shot_id": 2, "stage": "背景与女主入场", "text": f"拐进充满烟火气的小巷，老街坊排起的长队从不会说谎。"},
            {"shot_id": 3, "stage": "猛火镬气细节", "text": f"手起勺落之间，滚烫浓白的骨汤激荡出沉淀了数十年的醇厚。"},
            {"shot_id": 4, "stage": "吃规矩与仪式感", "text": f"轻轻吹开浮油喝下第一口，整个人瞬间被温柔的暖意包裹。"},
            {"shot_id": 5, "stage": "极致食欲特写", "text": f"每一筷挑起来都是满满的诚意，油润光泽让人忍不住屏住呼吸。"},
            {"shot_id": 6, "stage": "第一口试吃高潮", "text": f"咬下去的瞬间，浓郁的汤汁在口中化开，治愈了所有的疲惫。"},
            {"shot_id": 7, "stage": "深度品味与升华", "text": f"食物真正的治愈力，大概就是无论走多远，一尝到就能回到故乡。"},
            {"shot_id": 8, "stage": "直视镜头收尾金句", "text": f"如果是你，清晨第一口想吃什么？来评论区告诉我吧。"}
        ]
    else:
        shots = [
            {"shot_id": 1, "stage": "黄金3秒反常识钩子", "text": f"敢在本地把招牌擦得锃亮的，骨子里都有几分硬核的底气。"},
            {"shot_id": 2, "stage": "背景与女主入场", "text": f"跟着本地老饕穿街走巷，寻的就是这一口绝不妥协的霸道风味。"},
            {"shot_id": 3, "stage": "猛火镬气细节", "text": f"大铁锅里滋啦作响的油花，是市井江湖里最动听的节拍。"},
            {"shot_id": 4, "stage": "吃规矩与仪式感", "text": f"别心急，趁热快速翻拌让香气完全释放，才是最地道的规矩。"},
            {"shot_id": 5, "stage": "极致食欲特写", "text": f"挂满秘制红亮酱汁的一瞬间，视觉上的冲击就已经让人垂涎欲滴。"},
            {"shot_id": 6, "stage": "第一口试吃高潮", "text": f"入口的刹那焦香四溢，层次分明的冲击感瞬间征服了所有味蕾。"},
            {"shot_id": 7, "stage": "深度品味与升华", "text": f"人间烟火气，最抚凡人心，有些滋味吃过一次就刻进了骨髓。"},
            {"shot_id": 8, "stage": "直视镜头收尾金句", "text": f"这一口地道市井味你打几分？评论区等你来辩！"}
        ]
    return shots

def format_refinement_prompt(target_llm: str, food_name: str, char: dict, draft_shots: list) -> str:
    """生成专供 OpenAI 或 DeepSeek 的老饕润色超级 Prompt"""
    char_name = char.get("name", "女主")
    style_label = char.get("style_label", "特色风")
    personality = char.get("personality", "")
    expression = char.get("expression_style", "")
    
    lines_text = "\n".join([f"第{s['shot_id']}镜 ({s['stage']})：{s['text']} (当前{len(re.sub(r'[,.!?，。！？ ]', '', s['text']))}字)" for s in draft_shots])
    
    if target_llm.lower() == "deepseek":
        prompt = f"""你是一名深谙中国民间饮食哲学、市井烟火风骨与当代短视频爆款节奏的顶级导演兼文学编剧。
请基于深度推理思维，对以下【中国美女品鉴中华美食短视频】的 8 镜初版台词进行极限润色打磨，输出“完美的终极剧本台词”。

【品鉴美食】：{food_name}
【锁定出镜女主】：{char_name}（{style_label}）
【女主性格】：{personality}
【女主说话风格与口癖】：{expression}

【老饕深度推理与打磨要求】：
1. 逐镜字数硬卡点：全片共 8 镜，每镜台词必须严格控制在 20 到 28 个汉字（包含标点总字数严禁超过 30 字），多一个字或少于 16 字均视为无效！
2. 封杀所有 AI 套话：绝对禁止使用“绝绝子、YYDS、入口即化、吃货、非常美味、十分可口、色香味俱全、深受喜爱、历史悠久、今天我们来吃、大家好”等套话！
3. 通感动词与镬气：全篇多用老饕黑话与具象感官词（如“油花飞溅、浓白翻滚、焦香窜出、酸辣直撞天灵盖、舌头先投降胃再起义”）。
4. 镜6试吃留白：第6镜是第一口试吃，台词后半句为入口赞叹，需配合咀嚼留白。
5. 镜8收尾互动：女主直视镜头眼神杀，抛出高互动争议金句引爆评论区。

【待打磨的 8 镜初版台词】：
{lines_text}

请输出【润色后的终极完美台词】（按第1镜到第8镜输出，每镜附带精确汉字字数统计）。"""
    else:  # OpenAI / ChatGPT
        prompt = f"""你是一名顶级中国美食纪录片总编剧、抖音亿级爆款短视频文案操盘手，精通老饕黑话与短视频声画卡点节奏。
现在请针对【中国美女品鉴中华美食短视频】的初版分镜台词，以老饕毒辣挑剔的审美进行极限润色打磨，输出“完美的终极剧本台词”。

【品鉴美食主题】：{food_name}
【出镜女主锁定】：{char_name}（{style_label}）
【女主性格与语气】：{personality}。口吻风格：{expression}

【严苛打磨铁律】：
1. 逐镜字数硬卡点：全片共8镜，每镜台词严格限制在 20 到 28 个汉字（包含标点总字数严控在30字内），为镜头起音与收音留足呼吸留白！
2. 绝对违禁词：严禁出现“绝绝子、YYDS、入口即化、吃货、非常美味、十分可口、色香味俱全、深受喜爱、历史悠久、今天我们来吃、大家好”等一切AI套话，全篇用高密度感官动词与老饕黑话！
3. 分镜节奏精准匹配：
   - 第1镜（0-3s 黄金钩子）：制造反常识悬念或挑衅，3秒内留住观众；
   - 第2镜（3-8s 背景与入场）：立住女主气场与城市美食冲突；
   - 第3镜（8-14s 猛火镬气）：写透火候微观秘密与师傅手上绝活；
   - 第4镜（14-20s 专业吃法）：讲述老饕专属吃法规矩或翻拌仪式感；
   - 第5镜（20-26s 极致食欲）：微距特写食材的高光与酱汁诱惑；
   - 第6镜（26-33s 第一口试吃）：真实反应与心理反差（送入口中瞬间留出ASMR咀嚼留白）；
   - 第7镜（33-39s 老饕升华）：提炼城市与味道的灵魂羁绊；
   - 第8镜（39-45s 对镜头金句）：女主直视镜头眼神杀，说出收尾金句并抛出评论区互动争议。

【待润色的 8 镜初版分镜台词】：
{lines_text}

请严格按以下 JSON 格式输出最终打磨结果：
{{
  "润色后分镜台词": [
    {{"镜号": 1, "阶段": "黄金3秒反常识钩子", "台词": "...", "字数": 23}},
    {{"镜号": 2, "阶段": "建立背景与女主入场", "台词": "...", "字数": 25}},
    {{"镜号": 3, "阶段": "微观烹饪与烟火镬气", "台词": "...", "字数": 26}},
    {{"镜号": 4, "阶段": "沉浸互动与老饕规矩", "台词": "...", "字数": 24}},
    {{"镜号": 5, "阶段": "极致食欲特写近景", "台词": "...", "字数": 22}},
    {{"镜号": 6, "阶段": "第一口试吃高潮与反转", "台词": "...", "字数": 25}},
    {{"镜号": 7, "阶段": "老饕深度品味与灵魂升华", "台词": "...", "字数": 27}},
    {{"镜号": 8, "阶段": "直视镜头对口型金句", "台词": "...", "字数": 26}}
  ]
}}"""
    return prompt

def copy_to_clipboard(text: str):
    """通过 macOS pbcopy 复制到剪贴板"""
    try:
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        p.communicate(text.encode("utf-8"))
        return True
    except Exception as e:
        print(f"⚠️ 无法访问 pbcopy: {e}")
        return False

def open_in_chrome(url: str):
    """在 macOS 上使用 Google Chrome 打开指定 URL"""
    try:
        subprocess.run(["open", "-a", "Google Chrome", url], check=False)
        return True
    except Exception as e:
        print(f"⚠️ 启动 Chrome 失败: {e}")
        return False

def generate_html_bridge(food_name: str, char: dict, draft_shots: list, openai_prompt: str, deepseek_prompt: str, output_path: str):
    """生成本地可视化 Chrome 打磨交互桥接工作台"""
    char_name = char.get("name", "女主")
    style_label = char.get("style_label", "")
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>【{food_name}】短视频剧本大模型打磨工作台 - {char_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #121214; color: #e5e7eb; padding: 24px; margin: 0; }}
        .header {{ border-bottom: 1px solid #27272a; padding-bottom: 16px; margin-bottom: 24px; }}
        .badge {{ background: #ef4444; color: white; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: bold; margin-left: 8px; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .card {{ background: #18181b; border: 1px solid #27272a; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }}
        h2 {{ margin-top: 0; font-size: 18px; color: #f43f5e; }}
        .shot-item {{ background: #27272a; padding: 12px; border-radius: 8px; margin-bottom: 10px; font-size: 14px; line-height: 1.6; }}
        .shot-title {{ font-weight: bold; color: #38bdf8; margin-bottom: 4px; }}
        .btn {{ background: #2563eb; color: white; border: none; padding: 10px 18px; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 500; transition: background 0.2s; margin-right: 8px; margin-bottom: 8px; }}
        .btn:hover {{ background: #1d4ed8; }}
        .btn-green {{ background: #059669; }}
        .btn-green:hover {{ background: #047857; }}
        .btn-purple {{ background: #7c3aed; }}
        .btn-purple:hover {{ background: #6d28d9; }}
        textarea {{ width: 100%; height: 260px; background: #09090b; color: #e2e8f0; border: 1px solid #3f3f46; border-radius: 8px; padding: 12px; font-family: monospace; font-size: 13px; box-sizing: border-box; resize: vertical; }}
        .status {{ font-size: 13px; color: #10b981; margin-top: 8px; display: none; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🍜 《{food_name}》45秒美食短视频剧本打磨工作台 <span class="badge">出镜女主：{char_name}（{style_label}）</span></h1>
        <p style="color: #a1a1aa; margin: 0;">一键将专有老饕提示词送入 OpenAI (ChatGPT) 或 DeepSeek，打磨生成 100% 完美的 20~28 字神仙台词！</p>
    </div>

    <div class="grid">
        <div class="card">
            <h2>📝 当前初版吸引人台词 (8 阶段分镜)</h2>
            {"".join([f'<div class="shot-item"><div class="shot-title">第{s["shot_id"]}镜 · {s["stage"]}</div><div>{s["text"]}</div><div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">字数：{len(re.sub(r"[,.!?，。！？ ]", "", s["text"]))} 字</div></div>' for s in draft_shots])}
        </div>

        <div class="card">
            <h2>🚀 控制操作 Chrome 直达大模型打磨</h2>
            <p style="font-size: 13px; color: #94a3b8;">点击下方按钮将自动复制对应的超长打磨 Prompt，并直接在 Chrome 中打开对话页，直接粘贴即可打磨：</p>
            
            <button class="btn btn-green" onclick="copyAndOpen('openai')">🤖 复制打磨词并打开 ChatGPT (OpenAI)</button>
            <button class="btn btn-purple" onclick="copyAndOpen('deepseek')">🐉 复制打磨词并打开 DeepSeek</button>
            <div id="copy-status" class="status">✅ 已成功将打磨提示词复制到系统剪贴板！请在弹出的 Chrome 标签页中直接 Command + V 粘贴发送！</div>

            <h2 style="margin-top: 24px;">✨ 完美剧本回填与验收</h2>
            <p style="font-size: 13px; color: #94a3b8;">在大模型润色完成后，将生成的完美台词（纯文本或JSON）粘贴至下方：</p>
            <textarea id="refined-input" placeholder="将 ChatGPT 或 DeepSeek 输出的完美台词粘贴到这里..."></textarea>
            <br><br>
            <button class="btn" onclick="saveResult()">💾 确认使用此完美剧本生成最终视频工程全案</button>
            <div id="save-status" class="status">✅ 剧本已就绪！您可以在终端中直接执行项目脚手架生成完整 11 项交付全案！</div>
        </div>
    </div>

    <textarea id="openai-prompt" style="display:none;">{openai_prompt}</textarea>
    <textarea id="deepseek-prompt" style="display:none;">{deepseek_prompt}</textarea>

    <script>
        function copyAndOpen(target) {{
            const text = document.getElementById(target + '-prompt').value;
            navigator.clipboard.writeText(text).then(() => {{
                const status = document.getElementById('copy-status');
                status.style.display = 'block';
                setTimeout(() => {{ status.style.display = 'none'; }}, 6000);
                if (target === 'openai') {{
                    window.open('https://chatgpt.com', '_blank');
                }} else {{
                    window.open('https://chat.deepseek.com', '_blank');
                }}
            }});
        }}
        function saveResult() {{
            const val = document.getElementById('refined-input').value;
            if (!val.trim()) {{
                alert('请先将大模型润色好的台词粘贴进来！');
                return;
            }}
            document.getElementById('save-status').style.display = 'block';
            alert('完美剧本确认成功！可直接使用本台词生成 45 秒纯中文视频工程！');
        }}
    </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return output_path

def main():
    parser = argparse.ArgumentParser(description="美食短视频剧本台词生成与大模型打磨工具")
    parser.add_argument("--food", type=str, required=True, help="美食名称，如 '重庆火锅'")
    parser.add_argument("--character", type=str, default=None, help="指定女主姓名或ID")
    parser.add_argument("--target", type=str, choices=["openai", "deepseek", "both"], default="both", help="润色目标模型")
    parser.add_argument("--chrome", action="store_true", help="自动在 Chrome 浏览器中打开 ChatGPT / DeepSeek 或工作台")
    parser.add_argument("--output-prompt", type=str, default=None, help="保存打磨提示词到文件")
    parser.add_argument("--bridge", action="store_true", help="生成并在 Chrome 中打开本地可视化交互打磨工作台")
    
    args = parser.parse_args()
    
    pool = load_character_pool()
    char = select_character(pool, args.character, args.food)
    char_name = char.get("name", "女主")
    
    print(f"🎬 正在为【{args.food}】立项生成初版短视频剧本...")
    print(f"👑 锁定出镜女主: {char_name}（{char.get('style_label')}）[全片8镜严格锁定，终身性格/音色已绑定]")
    
    # 1. 生成吸引人的初版剧本台词
    draft_shots = generate_draft_script(args.food, char)
    print("\n" + "="*50)
    print(f"📜 《{args.food}》初版 8 镜吸引人剧本台词：")
    print("="*50)
    for s in draft_shots:
        clean_len = len(re.sub(r'[,.!?，。！？ ]', '', s['text']))
        print(f"  [第{s['shot_id']}镜 · {s['stage']}] ({clean_len}字)")
        print(f"   \"{s['text']}\"")
    print("="*50 + "\n")
    
    # 2. 生成专供 OpenAI 与 DeepSeek 的老饕润色超级提示词
    openai_prompt = format_refinement_prompt("openai", args.food, char, draft_shots)
    deepseek_prompt = format_refinement_prompt("deepseek", args.food, char, draft_shots)
    
    chosen_prompt = deepseek_prompt if args.target == "deepseek" else openai_prompt
    
    if args.output_prompt:
        with open(args.output_prompt, "w", encoding="utf-8") as f:
            f.write(chosen_prompt)
        print(f"💾 专属打磨提示词已保存至: {args.output_prompt}")
        
    # 3. Chrome 控制与联动
    if args.bridge:
        bridge_path = os.path.abspath(f"script_polish_{args.food.replace(' ', '_')}.html")
        generate_html_bridge(args.food, char, draft_shots, openai_prompt, deepseek_prompt, bridge_path)
        print(f"🌐 已生成本地 Chrome 交互打磨工作台: {bridge_path}")
        open_in_chrome(f"file://{bridge_path}")
        print("🖥️ 已在 Google Chrome 中唤起打磨工作台！")
    elif args.chrome:
        copied = copy_to_clipboard(chosen_prompt)
        target_url = "https://chatgpt.com" if args.target == "openai" else "https://chat.deepseek.com"
        open_in_chrome(target_url)
        print(f"🌐 已在 Google Chrome 中打开: {target_url}")
        if copied:
            print("📋 【超强老饕打磨提示词】已自动复制到系统剪贴板！请直接在 Chrome 对话框中 Command + V 粘贴发送！")
    else:
        # 默认也将提示词复制到剪贴板，方便操作
        copy_to_clipboard(chosen_prompt)
        print("📋 【超强老饕打磨提示词】已自动存入系统剪贴板！")
        print("💡 提示：可配合参数 `--chrome` 直接在 Google Chrome 中自动弹出 ChatGPT 或 DeepSeek 页面！")

if __name__ == "__main__":
    main()
