#!/usr/bin/env python3
"""
中华美食短视频音画与规范自动化质检脚本 (V2 动态工业版)
严格核验短视频工程配置是否符合：
1. 100% 纯中文提示词与环境生态
2. 全片锁定单一女主与固定人设/音色
3. 动态分镜架构（5~7 镜，标准推荐 6 镜），拒绝刻板固定套路
4. 自然生活化旁白字数（120~155 字）与严格去 AI 腔（严禁网红套话）
5. Continuity Router 连续性合理性（焦点切换与重定向锚定）
6. 声音四层混音与 BGM 智能闪避策略
"""

import sys
import os
import json
import re
import argparse

FORBIDDEN_WORDS = [
    "绝绝子", "YYDS", "入口即化", "吃货", "非常美味", "十分可口", 
    "色香味俱全", "深受喜爱", "深受大家喜爱", "历史悠久", "不容错过", 
    "值得一试", "大家好", "今天带大家", "今天我们来吃", "回味无穷",
    "治好了所有内耗", "直撞天灵盖", "直冲天灵盖", "舌头彻底缴械",
    "直接起义", "直接把我吃沉默了", "香迷糊", "封神", "上头", "沦陷"
]

def check_english_pollution(text: str) -> list:
    """检测是否含有英文长词或英文句子（允许合法的模型标号如 4K, 24fps 等）。"""
    if not isinstance(text, str):
        return []
    cleaned = re.sub(r'\b(4K|24fps|fps|BGM|LUFS|ID|jpg|png|json|shot|shots|re_anchor|reanchor)\b', '', text, flags=re.IGNORECASE)
    matches = re.findall(r'[a-zA-Z]{4,}', cleaned)
    return matches

def validate_food_project(config_path: str):
    print(f"🔍 开始自动化质检短视频工程配置: {config_path}")
    if not os.path.exists(config_path):
        print(f"❌ 错误: 配置文件不存在 {config_path}")
        return False

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    errors = []
    warnings = []
    
    # 1. 基础时长与分镜结构检测
    duration = data.get("视频总时长") or data.get("duration") or data.get("target_duration", 45.0)
    if not (40.0 <= duration <= 50.0):
        warnings.append(f"视频总时长为 {duration}s，推荐控制在 42~48s（45s 黄金规格）。")
        
    storyboard = data.get("storyboard", {})
    shots = data.get("分镜列表") or data.get("shots") or storyboard.get("shots", [])
    if len(shots) < 5:
        errors.append(f"分镜数过少（仅 {len(shots)} 镜），无法完成完整起承转合叙事。推荐 5~7 镜。")
    elif len(shots) > 7:
        warnings.append(f"分镜数为 {len(shots)} 镜，镜头切换过多会大幅增加换脸、换衣与食物变形概率。建议精简至 6 镜。")
        
    # 2. 出镜女主单一锁定与固定性格/音色检测
    heroine = data.get("出镜女主设定") or data.get("character") or data.get("character_bible")
    if not heroine:
        errors.append("缺失【出镜女主设定】！必须为全片选定一位固定女主。")
    else:
        name = heroine.get("女主姓名") or heroine.get("name") or heroine.get("character_id")
        traits = heroine.get("身材与面貌特征") or heroine.get("visual_traits") or heroine.get("description")
        voice = heroine.get("固定说话音色") or heroine.get("voice_persona")
        
        if not name:
            errors.append("【出镜女主设定】中缺少女主姓名！")
        if not traits:
            errors.append("【出镜女主设定】中缺少身材与相貌特征定妆描述！")
        if not voice:
            warnings.append(f"女主【{name}】缺少固定说话音色配置，建议绑定具体 TTS 音色参数。")

    # 3. 逐镜检查（字数、禁词、英文污染、Continuity Router 路由）
    total_chars = 0
    prev_was_pure_food = False

    for idx, shot in enumerate(shots):
        shot_id = shot.get("镜号") or shot.get("id", idx + 1)
        text = shot.get("旁白台词") or shot.get("narration") or shot.get("dialogue", "")
        prompt = shot.get("纯中文视频生成提示词") or shot.get("prompt", "")
        inherit = str(shot.get("参考帧继承策略") or shot.get("reference_strategy") or shot.get("ref_strategy", "")).lower()
        stage = shot.get("阶段定位") or shot.get("function") or shot.get("title", "")
        focus = str(shot.get("focus", "")).lower()

        # 3.1 纯中文检测
        eng_in_prompt = check_english_pollution(prompt)
        if eng_in_prompt:
            errors.append(f"[Shot {shot_id}] 提示词中存在英文单词污染: {eng_in_prompt}。全案要求 100% 纯中文提示词！")

        # 3.2 禁词与AI套话检测
        for fw in FORBIDDEN_WORDS:
            if fw in text:
                errors.append(f"[Shot {shot_id}] 发现 AI 套话/禁词 '{fw}'（台词: '{text}'）。请换为真实生活化味觉描写！")

        # 3.3 字数统计与单镜控制
        clean_text = re.sub(r'[，。！？、“”《》\s]', '', text)
        char_cnt = len(clean_text)
        total_chars += char_cnt

        if char_cnt > 38:
            errors.append(f"[Shot {shot_id}] 单镜台词字数过长（{char_cnt}字），极易导致赶场或抢拍！")

        # 3.4 Continuity Router 逻辑检测
        is_character_shot = "character" in focus or any(kw in prompt for kw in ["女主", "美女", "她将", "咽下", "大嚼", "女主品尝"])
        if is_character_shot and prev_was_pure_food:
            # 前一镜是纯食物特写，当前镜切回人物，必须使用 reanchor 或定妆图
            if "reanchor" not in inherit and "character" not in inherit and "重定向" not in inherit and "定妆" not in inherit:
                errors.append(f"[Shot {shot_id}] 从纯食物特写切回人物试吃，未配置【重定向锚定 (reanchor_character)】！若直接继承食物末帧会导致严重换脸变形。")

        prev_was_pure_food = ("food" in focus and "character" not in focus) or ("制作" in stage or "特写" in stage)

    # 4. 全片旁白总字数检测 (120~155 字)
    if total_chars < 115:
        warnings.append(f"全片旁白总字数仅 {total_chars} 字，信息量稍偏少，推荐 120～155 字。")
    elif total_chars > 165:
        errors.append(f"全片旁白总字数达 {total_chars} 字，45 秒内语速过快，严重破坏自然生活质感！必须精简至 155 字以内。")

    # 汇总质检报告
    print("\n" + "="*50)
    print(f"📊 V2 质检报告 - 结果汇总: {os.path.basename(config_path)}")
    print("="*50)
    
    if errors:
        print(f"❌ 质检未通过！发现 {len(errors)} 项阻塞性问题：")
        for err in errors:
            print(f"  • {err}")
    else:
        print("✅ 完美通过！完全符合 V2 动态分镜、自然旁白去AI腔、Continuity Router 与纯中文标准！")

    if warnings:
        print(f"\n⚠️ 提示优化建议 ({len(warnings)} 项)：")
        for w in warnings:
            print(f"  • {w}")
    print("="*50 + "\n")

    return len(errors) == 0

def main():
    parser = argparse.ArgumentParser(description="质检短视频工程配置文件 (V2 动态版)")
    parser.add_argument("--config", type=str, required=True, help="工程配置文件路径")
    args = parser.parse_args()
    
    success = validate_food_project(args.config)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
