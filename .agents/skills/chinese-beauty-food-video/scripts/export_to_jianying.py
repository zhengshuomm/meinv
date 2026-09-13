#!/usr/bin/env python3
"""
剪映 Pro 竖屏短视频自动化草稿导出管线 (JianYing Pro Draft Export Pipeline)
- 9:16 竖屏 (1080x1920) 电影级画幅初始化；
- 自动化多轨编排：视频轨 (MainVideo) + 女主第一人称台词人声轨 (SpokenVoice) + 字幕轨 (Subtitles) + 背景音乐轨 (BGM)；
- 支持 edge-tts 批量合成每镜女主专属音色干音并按时序精确放置；
- 生成符合剪映 v5.9+ 标准的 draft_info.json、draft_meta_info.json 与素材自包含体系；
- 无缝对接剪映官方「智能对口型」引擎，提供标准化操作 SOP。
"""

import os
import sys
import json
import asyncio
import argparse
import subprocess

WORKSPACE_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
bin_dir = os.path.join(WORKSPACE_ROOT, "bin")
if os.path.exists(bin_dir) and bin_dir not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{bin_dir}:{os.environ.get('PATH', '')}"

# 导入 jianying-editor skill
skill_root = os.path.join(WORKSPACE_ROOT, ".agents", "skills", "jianying-editor")
if not os.path.exists(skill_root):
    raise ImportError(f"未找到 jianying-editor skill: {skill_root}")

sys.path.insert(0, os.path.join(skill_root, "scripts"))
from jy_wrapper import JyProject
from utils.formatters import safe_tim

def resolve_drafts_root(custom_root=None):
    """智能解析剪映草稿存放路径"""
    if custom_root and os.path.exists(custom_root):
        return custom_root
    
    env_root = os.getenv("JY_PROJECTS_ROOT", "").strip()
    if env_root and os.path.exists(env_root):
        return env_root

    # 默认尝试 macOS 官方草稿路径
    mac_default = os.path.expanduser("~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft")
    try:
        if not os.path.exists(mac_default):
            os.makedirs(mac_default, exist_ok=True)
        # 测试写权限
        test_file = os.path.join(mac_default, ".perm_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return mac_default
    except Exception:
        pass

    # 工作区平滑退避路径
    workspace_drafts = os.path.join(WORKSPACE_ROOT, "drafts")
    os.makedirs(workspace_drafts, exist_ok=True)
    return workspace_drafts

def generate_fallback_silence(output_path: str, duration: float = 3.0, sr: int = 24000):
    """生成本地微小静音/白底占位音频 (WAV)，确保离线时依然可建立完整剪映音频轨"""
    import wave
    import struct
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    n_samples = int(duration * sr)
    # 转换为 wav 路径
    wav_path = output_path if output_path.endswith(".wav") else output_path.replace(".mp3", ".wav")
    with wave.open(wav_path, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sr)
        for _ in range(n_samples):
            wav_file.writeframes(struct.pack("<h", 0))
    return wav_path

async def synthesize_shot_audio(text: str, voice_name: str, rate: str, pitch: str, output_path: str):
    """调用 edge-tts 生成单句女主台词干音，若离线或沙盒受阻则优雅降级为本地占位音频"""
    try:
        import edge_tts
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        communicate = edge_tts.Communicate(text, voice=voice_name, rate=rate, pitch=pitch)
        await communicate.save(output_path)
        return output_path
    except Exception as e:
        print(f"  ⚠️ TTS 在线合成提示: 网络离线或沙盒限制 ({e})，启用本地占位音频")
        wav_path = generate_fallback_silence(output_path, duration=max(2.5, len(text) * 0.22))
        return wav_path

def get_audio_duration_seconds(audio_path: str) -> float:
    """使用 ffprobe 获取音频实际物理时长"""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", audio_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            return float(res.stdout.strip())
    except Exception:
        pass
    return 3.0

def export_project_to_jianying(config_path: str, custom_draft_name: str = None, custom_drafts_root: str = None, synthesize_tts: bool = True):
    """主导出函数：解析项目配置并生成剪映工程"""
    if not os.path.isabs(config_path):
        config_path = os.path.normpath(os.path.join(WORKSPACE_ROOT, config_path))

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    project_id = config.get("project_id", "food_video_project")
    food_title = config.get("food_title") or config.get("title") or "中华地道美食"
    char_info = config.get("character", {})
    char_name = char_info.get("女主姓名") or char_info.get("name") or "女主"
    voice_info = char_info.get("voice_persona", {})
    voice_name = voice_info.get("voice_name", "zh-CN-XiaoxiaoNeural")
    rate = voice_info.get("rate", "+0%")
    pitch = voice_info.get("pitch", "+0Hz")

    draft_name = custom_draft_name or f"【美食品鉴】{food_title}_{char_name}"
    drafts_root = resolve_drafts_root(custom_drafts_root)
    print(f"📁 目标草稿目录: {drafts_root}")
    print(f"🎬 初始化 9:16 竖屏工程: {draft_name}")

    # 初始化 9:16 竖屏 (1080x1920) 剪映工程
    project = JyProject(
        project_name=draft_name,
        width=1080,
        height=1920,
        drafts_root=drafts_root,
        overwrite=True
    )

    shots = config.get("shots") or config.get("storyboard", {}).get("shots", [])
    if not shots:
        raise ValueError("配置文件中未包含任何分镜数据 (shots)")

    audio_dir = os.path.join(WORKSPACE_ROOT, "tmp", "audio", project_id)
    os.makedirs(audio_dir, exist_ok=True)

    current_timeline_time = 0.0 # 秒

    print(f"🎞️ 正在排布分镜音视频轨道与字幕 (共 {len(shots)} 镜)...")

    for s in shots:
        shot_id = s.get("id") or s.get("镜号", 1)
        duration = float(s.get("duration") or (float(s.get("end", 6.0)) - float(s.get("start", 0.0))))
        dialogue = s.get("dialogue_cn") or s.get("dialogue") or s.get("旁白台词") or s.get("narration", "")

        # 视频素材路径
        video_filename = f"{project_id}_shot{shot_id}.mp4"
        video_path = os.path.join(WORKSPACE_ROOT, "tmp", "videos", video_filename)
        
        # 1. 添加视频片段到主视频轨 (强制 volume=0.0 静音，彻底消除 Veo 原生假英文/洋腔杂音)
        if os.path.exists(video_path):
            project.add_media_safe(
                video_path,
                start_time=f"{current_timeline_time:.3f}s",
                duration=f"{duration:.3f}s",
                track_name="MainVideo",
                volume=0.0
            )
            print(f"  ✅ [Shot {shot_id}] 已导入实拍视频 (已强制静音消除洋腔): {video_filename} ({duration:.1f}s)")
        else:
            print(f"  ℹ️ [Shot {shot_id}] 视频文件尚未生成，已在时间轴预留 {duration:.1f}s 槽位 (预设静音)")

        # 2. 合成并导入女主第一人称台词配音到音频轨
        if dialogue and synthesize_tts:
            audio_path = os.path.join(audio_dir, f"shot{shot_id}_dialogue.mp3")
            if not os.path.exists(audio_path):
                audio_path = asyncio.run(synthesize_shot_audio(dialogue, voice_name, rate, pitch, audio_path))
            
            audio_dur = get_audio_duration_seconds(audio_path)
            # 音频起音留白 0.15 秒，更显自然呼吸感
            audio_start = current_timeline_time + 0.15
            project.add_media_safe(
                audio_path,
                start_time=f"{audio_start:.3f}s",
                duration=f"{audio_dur:.3f}s",
                track_name="SpokenVoice"
            )
            print(f"  🎙️ [Shot {shot_id}] 已导入台词音频: {os.path.basename(audio_path)} ({audio_dur:.2f}s)")

        # 3. 添加字幕到字幕轨 (居中靠底安全区，白字黑描边)
        if dialogue:
            sub_start = current_timeline_time + 0.15
            # 字幕时长与音频相当或略长
            sub_dur = min(duration - 0.3, max(2.5, len(dialogue) * 0.22))
            project.add_text_simple(
                text=dialogue,
                start_time=f"{sub_start:.3f}s",
                duration=f"{sub_dur:.3f}s",
                track_name="Subtitles"
            )
            sub_preview = dialogue[:15]
            print(f"  📝 [Shot {shot_id}] 已挂载中文大字字幕: '{sub_preview}...'")

        current_timeline_time += duration

    # 保存工程
    result = project.save()
    draft_dir = os.path.join(drafts_root, project.name)

    print("\n" + "=" * 70)
    print(f"🎉 [剪映 Pro 竖屏草稿导出成功！]")
    print(f"📌 草稿工程名称: {project.name}")
    print(f"📂 本地草稿路径: {draft_dir}")
    print(f"⏱️ 视频总时长:   {current_timeline_time:.1f} 秒 (9:16 竖屏 1080x1920)")
    print(f"👸 出镜女主声音: {char_name} ({voice_name})")
    print("-" * 70)
    print("👉 剪映官方【智能对口型】一键合流操作指南 (SOP):")
    print("  1. 打开「剪映 Pro」桌面客户端；")
    print(f"  2. 在草稿列表中，直接点击打开新建的草稿「{project.name}」；")
    print("  3. 此时 9:16 视频轨、女主口播台词轨与字幕轨已按 6 镜时序排布完毕；")
    print("  4. 选中时间轴上女主出镜的分镜视频片段；")
    print("  5. 鼠标右键点击该视频片段，选择「智能对口型」（或点击右侧面板「音频」->「智能对口型」）；")
    print("  6. 剪映官方引擎将全自动根据下方台词音频，将女主唇形与中文发音 100% 同步对齐；")
    print("  7. 一键点击右上角「导出」，即获电影级高清成品！")
    print("=" * 70 + "\n")

    return {
        "status": "SUCCESS",
        "draft_name": project.name,
        "draft_dir": draft_dir,
        "total_duration": current_timeline_time
    }

def main():
    parser = argparse.ArgumentParser(description="剪映 Pro 竖屏短视频自动化草稿导出管线")
    parser.add_argument("--config", type=str, required=True, help="项目 JSON 配置文件路径")
    parser.add_argument("--name", type=str, default=None, help="自定义剪映草稿名称")
    parser.add_argument("--drafts-root", type=str, default=None, help="自定义剪映草稿根目录")
    parser.add_argument("--no-tts", action="store_true", help="跳过 TTS 语音生成")
    args = parser.parse_args()

    export_project_to_jianying(
        config_path=args.config,
        custom_draft_name=args.name,
        custom_drafts_root=args.drafts_root,
        synthesize_tts=not args.no_tts
    )

if __name__ == "__main__":
    main()
