#!/usr/bin/env python3
"""
全自动纯代码 AI 对口型与现场拟音融合管线 (Automated Python Lip-Sync & Acoustic Blending Pipeline)
- 完全免去手动操作剪映，纯 Python + Apple Silicon 本地驱动；
- 采用 Wav2Lip-GAN 高精唇动模型，根据标准母语普通话音频实时重塑口型；
- 画面保持清晰度、发型与服装；
- 智能声学融合：将标准台词干音与 Veo 现场炭火/夜市环境底噪按黄金比例融合，杜绝录音室抽离感。
"""

import os
import sys
import argparse
import subprocess
import shutil

SKILL_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
WORKSPACE_ROOT = os.path.normpath(os.path.join(SKILL_DIR, "..", "..", ".."))
TOOLS_DIR = os.path.join(SKILL_DIR, "tools", "wav2lip")
CHECKPOINT_PATH = os.path.join(TOOLS_DIR, "checkpoints", "wav2lip_gan.pth")
BIN_DIR = os.path.join(WORKSPACE_ROOT, "bin")

if os.path.exists(BIN_DIR) and BIN_DIR not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{BIN_DIR}:{os.environ.get('PATH', '')}"

def run_lipsync(video_path: str, audio_path: str, output_path: str, blend_ambient: bool = True):
    video_path = os.path.abspath(video_path)
    audio_path = os.path.abspath(audio_path)
    output_path = os.path.abspath(output_path)

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"视频文件不存在: {video_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"音频文件不存在: {audio_path}")
    if not os.path.exists(CHECKPOINT_PATH):
        raise FileNotFoundError(f"模型权重不存在: {CHECKPOINT_PATH}")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    temp_dir = os.path.join(WORKSPACE_ROOT, "tmp", "lipsync_cache")
    os.makedirs(temp_dir, exist_ok=True)

    raw_lipsync_video = os.path.join(temp_dir, "raw_lipsync.mp4")

    print(f"🚀 [全自动对口型] 正在启动 Wav2Lip-GAN 唇形重构...")
    print(f"  🎬 原始视频: {video_path}")
    print(f"  🎙️ 标准母语台词: {audio_path}")
    print(f"  🧠 运行设备: Apple Silicon 本地硬件加速")

    cmd = [
        sys.executable,
        os.path.join(TOOLS_DIR, "inference.py"),
        "--checkpoint_path", CHECKPOINT_PATH,
        "--face", video_path,
        "--audio", audio_path,
        "--outfile", raw_lipsync_video,
        "--pads", "0", "15", "0", "0",
        "--face_det_batch_size", "8",
        "--wav2lip_batch_size", "64",
        "--resize_factor", "1"
    ]

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{TOOLS_DIR}:{env.get('PYTHONPATH', '')}"

    proc = subprocess.run(cmd, cwd=TOOLS_DIR, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0 or not os.path.exists(raw_lipsync_video):
        print(f"⚠️ 原始分辨率推理提示，尝试轻量模式 (resize_factor=2)...")
        cmd[-1] = "2"
        proc2 = subprocess.run(cmd, cwd=TOOLS_DIR, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if proc2.returncode != 0 or not os.path.exists(raw_lipsync_video):
            raise RuntimeError(f"Wav2Lip 推理失败: {proc2.stdout[-500:]}")

    print("  ✅ 唇形重构计算完成！")

    if blend_ambient:
        print("  🎚️ 正在执行声学混音：融合现场夜市/炭火环境音，消除录音室违和感...")
        final_cmd = [
            "ffmpeg", "-y",
            "-i", raw_lipsync_video,
            "-i", video_path,
            "-filter_complex",
            "[0:a]volume=1.0[vocal];[1:a]volume=0.20,lowpass=f=2500[amb];[vocal][amb]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "libx264", "-crf", "18", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            output_path
        ]
    else:
        final_cmd = [
            "ffmpeg", "-y",
            "-i", raw_lipsync_video,
            "-c:v", "libx264", "-crf", "18", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            output_path
        ]

    subprocess.run(final_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"🎉 [完成] 全自动对口型成片已保存至: {output_path}")
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="全自动免剪映 AI 对口型工具")
    parser.add_argument("--video", required=True, help="输入视频路径")
    parser.add_argument("--audio", required=True, help="输入标准发音音频路径")
    parser.add_argument("--out", required=True, help="输出 MP4 路径")
    parser.add_argument("--no-ambient", action="store_true", help="不融合原片环境音")
    args = parser.parse_args()

    run_lipsync(args.video, args.audio, args.out, blend_ambient=not args.no_ambient)
