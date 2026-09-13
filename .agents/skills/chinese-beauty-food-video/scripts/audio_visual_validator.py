#!/usr/bin/env python3
"""
中华美食短视频音画与规范自动化质检脚本 (Audio-Visual & Compliance Validator)
严格核验短视频工程配置是否符合：
1. 100% 纯中文环境（零英文污染检测）
2. 全片锁定单一女主与固定性格/音色设定
3. 抖音爆款中文BGM与智能闪避（Ducking）混音机制
4. 45秒黄金时长与8镜紧凑叙事节奏
5. 空镜重定向锚定准则（Re-anchor Rule）
6. 老饕台词字数与高密度感官词（严禁AI套话）
"""

import sys
import os
import json
import re
import argparse

FORBIDDEN_WORDS = [
    "绝绝子", "YYDS", "入口即化", "吃货", "非常美味", "十分可口", 
    "色香味俱全", "深受喜爱", "深受大家喜爱", "历史悠久", "不容错过", 
    "值得一试", "大家好", "今天带大家", "今天我们来吃", "回味无穷"
]

def check_english_pollution(text: str) -> list:
    """检测是否含有英文长词或英文句子（允许合法的模型标号如 4K, 24fps 等）。"""
    if not isinstance(text, str):
        return []
    # 过滤允许的技术缩写如 4K, 24fps, BGM, LUFS, ID, jpg, png, json
    cleaned = re.sub(r'\b(4K|24fps|fps|BGM|LUFS|ID|jpg|png|json)\b', '', text, flags=re.IGNORECASE)
    # 寻找连续4个以上字母的英文单词
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
    duration = data.get("视频总时长") or data.get("duration_seconds", 0)
    if not (40.0 <= duration <= 50.0):
        warnings.append(f"视频总时长为 {duration}s，推荐标准为 40~50s（45s 黄金时长）。")
        
    shots = data.get("分镜列表") or data.get("shots", [])
    if len(shots) < 6:
        errors.append(f"分镜数过少（仅 {len(shots)} 镜），45s 短视频标准要求 8 镜紧凑结构。")
    elif len(shots) != 8:
        warnings.append(f"分镜数为 {len(shots)} 镜，标准 45s 全案推荐严格 8 镜。")
        
    # 2. 出镜女主单一锁定与固定性格/音色检测
    heroine = data.get("出镜女主设定") or data.get("character_bible")
    if not heroine:
        errors.append("缺失【出镜女主设定】！必须为全片选定一位永久女主。")
    else:
        name = heroine.get("女主姓名") or heroine.get("name") or heroine.get("character_id")
        traits = heroine.get("身材与面貌特征") or heroine.get("visual_traits") or heroine.get("description")
        voice = heroine.get("固定说话音色") or heroine.get("voice_persona")
        personality = heroine.get("固定性格") or heroine.get("personality")
        
        if not name:
            errors.append("【出镜女主设定】中缺少女主姓名！")
        if not traits:
            errors.append("【出镜女主设定】中缺少身材与相貌特征定妆描述！")
        if not voice:
            errors.append(f"女主【{name}】缺少固定说话音色配置（TTS音色、语速），严禁随意更换口音！")
        if not personality:
            warnings.append(f"女主【{name}】缺少固定性格定位。")

    # 3. 抖音爆款中文BGM与智能闪避策略检测
    bgm_config = data.get("抖音爆款背景音乐配置") or data.get("bgm_config")
    if not bgm_config:
        warnings.append("未配置【抖音爆款背景音乐配置】！推荐为短视频配置地道中文爆款BGM以获取流量推荐。")
    else:
        track = bgm_config.get("推荐中文曲目") or bgm_config.get("track", "")
        ducking = bgm_config.get("智能闪避混音策略") or bgm_config.get("ducking_strategy", "")
        if not track:
            errors.append("背景音乐配置缺少【推荐中文曲目】！")
        if not ducking or ("闪避" not in ducking and "压低" not in ducking and "静音" not in ducking):
            warnings.append("背景音乐缺少智能闪避（Ducking）控制说明，易导致BGM喧宾夺主掩盖人声与ASMR！")

    # 4. 逐镜检查（字数、禁词、英文污染、首尾帧重定向）
    for idx, shot in enumerate(shots):
        shot_id = shot.get("镜号") or shot.get("shot_id", idx + 1)
        text = shot.get("旁白台词") or shot.get("narration", "")
        prompt = shot.get("纯中文视频生成提示词") or shot.get("prompt", "")
        inherit = shot.get("参考帧继承策略") or shot.get("frame_inheritance", "")
        stage = shot.get("阶段定位") or shot.get("stage", "")
        duration_shot = shot.get("时长") or shot.get("duration", 0)

        # 4.1 纯中文环境检测（零英文污染）
        eng_in_prompt = check_english_pollution(prompt)
        if eng_in_prompt:
            errors.append(f"[Shot {shot_id}] 提示词中存在英文单词污染: {eng_in_prompt}。本项目全流程要求 100% 纯中文提示词！")

        eng_in_text = check_english_pollution(text)
        if eng_in_text:
            errors.append(f"[Shot {shot_id}] 旁白台词中存在英文单词: {eng_in_text}！")

        # 4.2 禁词与AI套话检测
        for fw in FORBIDDEN_WORDS:
            if fw in text:
                errors.append(f"[Shot {shot_id}] 发现严苛禁词/AI套话 '{fw}'（台词: '{text}'）。必须替换为高密度感官实体词！")

        # 4.3 台词字数卡点 (15 ~ 32 字，最佳 20 ~ 28 字)
        clean_text = re.sub(r'[，。！？、“”《》\s]', '', text)
        char_cnt = len(clean_text)
        if char_cnt > 32:
            errors.append(f"[Shot {shot_id}] 台词字数过长（{char_cnt}字），在 {duration_shot}s 镜头内极易超速或抢拍！建议控制在 20~28 字。")
        elif char_cnt < 12 and shot_id != 1:
            warnings.append(f"[Shot {shot_id}] 台词字数偏少（{char_cnt}字），信息密度可能偏弱。")

        # 4.4 试吃高潮重定向锚定准则检测 (Re-anchor Rule)
        if shot_id == 6 or "试吃" in stage or "Tasting" in stage:
            inherit_str = str(inherit)
            if "重定向" not in inherit_str and "re_anchor" not in inherit_str and "回溯" not in inherit_str:
                errors.append(f"[Shot {shot_id}] 试吃高潮人像镜头未执行【重定向锚定准则】！严禁直接继承前镜纯食物特写，否则会引发突变或换脸！")

    # 5. 负向提示词检测
    neg_prompt = data.get("严苛负向约束") or data.get("negative_prompt", "")
    if not neg_prompt:
        warnings.append("缺少全局【严苛负向约束】（反变形、反换脸、反西方脸等）。")
    elif check_english_pollution(neg_prompt):
        errors.append("【严苛负向约束】中包含英文内容，请使用纯中文负向约束词！")

    # 汇总质检报告
    print("\n" + "="*50)
    print(f"📊 质检报告 - 结果汇总: {os.path.basename(config_path)}")
    print("="*50)
    
    if errors:
        print(f"❌ 质检未通过！发现 {len(errors)} 项阻塞性问题（必须纠正）：")
        for err in errors:
            print(f"  • {err}")
    else:
        print("✅ 完美通过！符合【全流程纯中文 + 单女主锁定 + 抖音BGM智能闪避 + 动画连贯】全部技术铁律！")

    if warnings:
        print(f"\n⚠️ 提示优化建议 ({len(warnings)} 项)：")
        for w in warnings:
            print(f"  • {w}")
    print("="*50 + "\n")

    return len(errors) == 0

def main():
    parser = argparse.ArgumentParser(description="质检短视频工程配置文件")
    parser.add_argument("--config", type=str, required=True, help="工程配置文件路径")
    args = parser.parse_args()
    
    success = validate_food_project(args.config)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
