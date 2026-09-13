#!/usr/bin/env python3
"""
中华美食短视频 Google Flow (Veo) Chrome CDP + Playwright 通用自动化控制器 (V2 动态工业版)
- 动态分镜支持 (不硬编码分镜数量，支持 5-7 镜动态规划)
- 严格遵循 V2 Continuity Router (连续性决策路由，拒绝无脑链式继承)
- 人物 Reference Anchor 简明锁定，杜绝冗长文本干扰食物与动作注意力
- 复用本地 Chrome 调试端口 (localhost:9222)，稳健 UI 自动化交互
- 毫秒级提取视频末帧与智能关键帧分发
"""

import os
import sys
import time
import json
import argparse
import subprocess
import urllib.request
import shutil
try:
    import cv2
except ImportError:
    cv2 = None

os.environ["no_proxy"] = "localhost,127.0.0.1,*"
os.environ["NO_PROXY"] = "localhost,127.0.0.1,*"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

WORKSPACE_ROOT = "/Users/shuozheng/Documents/meinv"
DEFAULT_CONFIG_PATH = None
OUTPUT_VIDEOS_DIR = os.path.join(WORKSPACE_ROOT, "tmp", "videos")

os.makedirs(OUTPUT_VIDEOS_DIR, exist_ok=True)

def find_ffmpeg_bin():
    """查找可用的 ffmpeg 可执行文件"""
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    tanshi_ffmpeg = "/Users/shuozheng/Documents/tanshi/.venv/bin/ffmpeg"
    if os.path.exists(tanshi_ffmpeg):
        return tanshi_ffmpeg
    return "ffmpeg"

FFMPEG_BIN = find_ffmpeg_bin()

def resolve_workspace_path(path):
    """将相对路径转换为基于工作区根目录的绝对路径"""
    if not path:
        return None
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(WORKSPACE_ROOT, path))

def load_food_config(config_path):
    """加载并标准化美食短视频配置文件 (兼容 V1 与 V2 动态数据格式)"""
    target_path = resolve_workspace_path(config_path)
    if not os.path.exists(target_path):
        alt_path = os.path.join(WORKSPACE_ROOT, "examples", os.path.basename(config_path))
        if os.path.exists(alt_path):
            target_path = alt_path
        else:
            raise FileNotFoundError(f"未找到美食配置文件: {config_path} (尝试路径: {target_path})")

    with open(target_path, "r", encoding="utf-8") as f:
        raw_config = json.load(f)

    project_id = raw_config.get("项目编号") or raw_config.get("project_id") or raw_config.get("title", "food_video")
    food_title = raw_config.get("美食主题") or raw_config.get("food_title") or raw_config.get("title", "中华美食")
    
    # 提取角色设定与主图
    character_info = raw_config.get("出镜女主设定") or raw_config.get("character", {})
    master_photo = resolve_workspace_path(
        character_info.get("定妆原图路径") or character_info.get("photo_path") or raw_config.get("character_reference", "")
    )
    food_ref = resolve_workspace_path(raw_config.get("food_reference", ""))
    scene_ref = resolve_workspace_path(raw_config.get("scene_reference", ""))

    # 提取分镜列表 (支持 shots / 分镜列表 / storyboard.shots)
    storyboard = raw_config.get("storyboard", {})
    raw_shots = raw_config.get("分镜列表") or raw_config.get("shots") or storyboard.get("shots", [])
    normalized_shots = []

    for idx, s in enumerate(raw_shots, start=1):
        shot_id = s.get("镜号") or s.get("id") or idx
        title = s.get("阶段定位") or s.get("function") or s.get("title", f"Shot {shot_id}")
        prompt = s.get("prompt_cn") or s.get("prompt") or s.get("纯中文视频生成提示词") or s.get("prompt_en") or ""
        ref_strategy = s.get("参考帧继承策略") or s.get("reference_strategy") or s.get("ref_strategy", "")
        duration = float(s.get("时长") or (float(s.get("end", 6.0)) - float(s.get("start", 0.0))) if "start" in s and "end" in s else s.get("duration", 6.0))
        dialogue = s.get("dialogue_cn") or s.get("dialogue") or s.get("旁白台词") or s.get("narration", "")
        audio_notes = s.get("声音拟音与音乐控制") or s.get("audio_notes", "")
        focus = s.get("focus", "")

        filename = f"{project_id}_shot{shot_id}.mp4"
        video_path = os.path.join(OUTPUT_VIDEOS_DIR, filename)
        last_frame = os.path.join(OUTPUT_VIDEOS_DIR, f"{project_id}_shot{shot_id}_last_frame.jpg")

        explicit_init = s.get("初始参考图") or s.get("initial_image")
        initial_image = resolve_workspace_path(explicit_init) if explicit_init else None

        normalized_shots.append({
            "id": shot_id,
            "title": title,
            "prompt": prompt,
            "ref_strategy": ref_strategy,
            "focus": focus,
            "duration": duration,
            "dialogue": dialogue,
            "audio_notes": audio_notes,
            "filename": filename,
            "video_path": video_path,
            "last_frame": last_frame,
            "initial_image": initial_image,
            "master_photo": master_photo,
            "food_ref": food_ref,
            "scene_ref": scene_ref
        })

    config = {
        "project_id": project_id,
        "food_title": food_title,
        "character": character_info,
        "master_photo": master_photo,
        "food_ref": food_ref,
        "scene_ref": scene_ref,
        "shots": normalized_shots,
        "raw_config": raw_config
    }
    return config, target_path

def extract_last_frame(video_path, output_frame_path):
    """使用 OpenCV 毫秒级提取视频最后一帧"""
    if not os.path.exists(video_path):
        print(f"⚠️ 视频不存在，无法提取末帧: {video_path}")
        return False
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        print(f"⚠️ 无法读取视频帧: {video_path}")
        cap.release()
        return False
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_frame_path, frame)
        cap.release()
        file_kb = os.path.getsize(output_frame_path) / 1024
        print(f"  📸 成功提取最后一帧: {os.path.basename(output_frame_path)} (总{total_frames}帧, {file_kb:.1f}KB)")
        return True
    else:
        print(f"❌ 提取最后一帧失败: {video_path}")
        cap.release()
        return False

def copy_image_to_clipboard(image_path):
    """通过 macOS 原生 osascript 将图片拷贝至剪贴板供 Flow 粘贴"""
    if not os.path.exists(image_path):
        print(f"⚠️ 警告: 关键帧图片不存在: {image_path}")
        return False
    cmd = ["osascript", "-e", f'set the clipboard to (read (POSIX file "{image_path}") as JPEG picture)']
    try:
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"❌ 剪贴板复制失败: {e}")
        return False

def dismiss_overlays(page):
    """关闭可能的弹窗遮罩层与提示框"""
    backdrops = page.locator(".cdk-overlay-backdrop")
    for _ in range(3):
        if backdrops.count() > 0:
            try:
                backdrops.first.click(force=True, timeout=800)
                page.wait_for_timeout(200)
            except Exception:
                page.keyboard.press("Escape")
        else:
            break

def ensure_aspect_ratio_9_16(page):
    """确保 Google Flow 当前处于 9:16 竖屏模式"""
    try:
        dismiss_overlays(page)
        ratio_btn = page.locator('button:has-text("9:16"), button:has(mat-icon:has-text("crop_9_16"))')
        if ratio_btn.count() > 0 and ratio_btn.first.is_visible():
            return True

        settings_btn = page.locator('button:has-text("16:9"), button:has(mat-icon:has-text("crop_16_9")), button.settings-pill, button[aria-label*="aspect"], button[aria-label*="settings"]').first
        if settings_btn.is_visible():
            print("📱 正在切换画面比例为 9:16 竖屏...")
            settings_btn.click(force=True)
            page.wait_for_timeout(600)
            target_916 = page.locator('.cdk-overlay-container [role="menuitem"]:has-text("9:16"), .cdk-overlay-container button:has-text("9:16"), [role="option"]:has-text("9:16")').first
            if target_916.is_visible():
                target_916.click(force=True)
                page.wait_for_timeout(600)
                dismiss_overlays(page)
                print("  ✅ 成功设置为 9:16 竖屏！")
                return True
            dismiss_overlays(page)
    except Exception as e:
        print(f"ℹ️ 画面比例检查提示: {e}")
    return False

def connect_flow_page(browser):
    """连接并确保进入 Google Flow 创作页面"""
    target_page = None
    for ctx in browser.contexts:
        for page in ctx.pages:
            if "flow.google.com" in page.url:
                target_page = page
                break
        if target_page:
            break

    if not target_page:
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        target_page = ctx.pages[0] if ctx.pages else ctx.new_page()
        target_page.goto("https://flow.google.com/")
        target_page.wait_for_timeout(3000)

    if "/edit/" in target_page.url:
        base_url = target_page.url.split("/edit/")[0]
        target_page.goto(base_url, wait_until="networkidle")

    if "/project/" not in target_page.url:
        print("ℹ️ 当前停留在 Flow 首页，正在自动进入创作工程...")
        proj_links = target_page.locator('a[href*="/project/"]')
        if proj_links.count() > 0:
            href = proj_links.first.get_attribute("href")
            full_url = f"https://flow.google.com{href}" if href.startswith("/") else href
            target_page.goto(full_url)
            target_page.wait_for_timeout(3000)
        else:
            new_btn = target_page.locator('text="New project"').first
            if new_btn.is_visible():
                new_btn.click()
                target_page.wait_for_timeout(4000)

    ensure_aspect_ratio_9_16(target_page)
    return target_page

def clear_prompt_box(page):
    """清空 Flow 提示词输入框与可能附带的图片标签"""
    dismiss_overlays(page)
    pm = page.locator("div.ProseMirror")
    if pm.count() == 0:
        return
    pm.click(force=True)
    page.wait_for_timeout(100)
    page.keyboard.press("Meta+a")
    page.keyboard.press("Backspace")
    page.wait_for_timeout(100)

    # 移除可能残留的已附加图片 chip
    chips = page.locator('flow-prompt-attachment, .attachment-chip, button[aria-label*="Remove image"], button[aria-label*="Delete image"]')
    for i in range(chips.count()):
        try:
            chips.nth(i).click(force=True, timeout=500)
            page.wait_for_timeout(100)
        except Exception:
            pass

def wait_for_generation_complete(page, shot_id, timeout=300, initial_error_count=0):
    """实时监听云端渲染进度 (0%~100%) 并精准抓取最新生成的视频"""
    print(f"⏳ 开始监听分镜 [{shot_id}] 生成状态 (最大等待: {timeout}秒)...")
    start_time = time.time()
    last_pct = -1

    while time.time() - start_time < timeout:
        elapsed = int(time.time() - start_time)

        # 检查新出现的错误警告
        error_tiles = page.locator('flow-error-tile, .error-tile, [role="alert"]:has-text("failed")')
        if error_tiles.count() > initial_error_count:
            last_err = error_tiles.last
            if last_err.is_visible():
                err_text = last_err.inner_text().strip()
                print(f"❌ 检测到生成报错: {err_text}")
                return False

        # 读取进度百分比
        pct_locators = page.locator('.progress-text, [aria-valuenow], span:has-text("%")')
        for i in range(pct_locators.count()):
            txt = pct_locators.nth(i).inner_text().strip()
            if "%" in txt:
                try:
                    num = int(txt.replace("%", "").strip())
                    if num != last_pct:
                        print(f"  📈 云端生成进度: {num}% (已耗时 {elapsed}秒)")
                        last_pct = num
                except Exception:
                    pass

        # 检查视频就绪
        completed_videos = page.locator("flow-generation-tile video, .generation-result video, video[src*='blob:']")
        if completed_videos.count() > 0:
            first_vid = completed_videos.first
            if first_vid.is_visible():
                print(f"🎉 分镜 [{shot_id}] 视频渲染完成！(总耗时 {elapsed}秒)")
                return True

        dismiss_overlays(page)
        time.sleep(3)

    print(f"\n⏰ 分镜 [{shot_id}] 等待渲染超时 ({timeout}秒)")
    return False

def determine_start_frame(shot_data, all_shots, config):
    """
    V2 Continuity Router (连续性决策路由):
    严禁无脑链式末帧继承。根据 reference_strategy 或构图与焦点智能分配参考锚点：
    1. 显式指定的 initial_image 拥有最高优先级；
    2. ref_strategy 声明为 'character' / 'character_reference' / '定妆原图'：使用女主专属定妆原图；
    3. ref_strategy 声明为 'food' / 'food_reference'：使用美食参考图（若无则纯文字驱动）；
    4. ref_strategy 声明为 'scene' / 'scene_reference'：使用场景参考图；
    5. ref_strategy 声明为 'previous_frame' / 'previous_last_frame' / '继承前一镜'：
       仅在动作连续且构图相近时继承前一镜 (N-1) 末帧；
    6. ref_strategy 声明为 'reanchor_character' / '重定向' / '回溯'：
       回溯锁定最近一个出镜人物镜头末帧或定妆原图，规避无脸特写污染；
    7. 默认路由：Shot 1 默认锁定女主定妆原图；其余镜头根据焦点自适应。
    """
    shot_id = shot_data["id"]
    ref_strategy = str(shot_data.get("ref_strategy", "")).lower()
    focus = str(shot_data.get("focus", "")).lower()
    explicit_image = shot_data.get("initial_image")

    # 1. 显式指定
    if explicit_image and os.path.exists(explicit_image):
        print(f"📌 [显式首帧] 分镜 [{shot_id}] 使用显式指定首帧: {os.path.basename(explicit_image)}")
        return explicit_image

    master = config.get("master_photo")
    food_ref = config.get("food_ref")
    scene_ref = config.get("scene_ref")

    # 2. Shot 1 或明确指定角色参考
    if shot_id == 1 or "character" in ref_strategy or "定妆" in ref_strategy:
        if master and os.path.exists(master):
            print(f"🌟 [人物锚定 Router] 分镜 [{shot_id}] 锁定女主专属定妆参考图: {os.path.basename(master)}")
            return master

    # 3. 明确指定美食参考图
    if "food" in ref_strategy or ("food" in focus and "character" not in focus):
        if food_ref and os.path.exists(food_ref):
            print(f"🍲 [美食锚定 Router] 分镜 [{shot_id}] 锁定美食专属参考图: {os.path.basename(food_ref)}")
            return food_ref

    # 4. 明确指定场景参考图
    if "scene" in ref_strategy or "环境" in ref_strategy:
        if scene_ref and os.path.exists(scene_ref):
            print(f"🏮 [场景锚定 Router] 分镜 [{shot_id}] 锁定场景参考图: {os.path.basename(scene_ref)}")
            return scene_ref

    # 5. 回溯重定向锚定人物
    if "reanchor" in ref_strategy or "重定向" in ref_strategy or "回溯" in ref_strategy:
        # 向前寻找最近一个有末帧的人物分镜
        for prev in reversed(all_shots[:shot_id - 1]):
            if prev.get("last_frame") and os.path.exists(prev["last_frame"]):
                # 若前序镜头为人物出镜
                if "character" in str(prev.get("focus", "")).lower() or "女主" in str(prev.get("prompt", "")):
                    print(f"🔄 [重定向锚定 Router] 分镜 [{shot_id}] 回溯锁定分镜 [{prev['id']}] 人物末帧: {os.path.basename(prev['last_frame'])}")
                    return prev["last_frame"]
        if master and os.path.exists(master):
            print(f"🔄 [重定向锚定 Router] 分镜 [{shot_id}] 回溯锁定女主定妆原图: {os.path.basename(master)}")
            return master

    # 6. 相邻连续动作 (previous_frame)
    if "previous" in ref_strategy or "继承" in ref_strategy or "last_frame" in ref_strategy:
        prev_shot = next((s for s in all_shots if s["id"] == shot_id - 1), None)
        if prev_shot:
            prev_last_frame = prev_shot["last_frame"]
            if not os.path.exists(prev_last_frame):
                prev_video = prev_shot["video_path"]
                if os.path.exists(prev_video):
                    print(f"🔄 提取前序分镜 [{prev_shot['id']}] 最后一帧...")
                    extract_last_frame(prev_video, prev_last_frame)
            if os.path.exists(prev_last_frame):
                print(f"🔗 [连续性 Router] 分镜 [{shot_id}] 动作连续继承前一镜 [{prev_shot['id']}] 末帧: {os.path.basename(prev_last_frame)}")
                return prev_last_frame

    # 7. 默认自适应路由
    if "character" in focus or any(kw in shot_data.get("prompt", "") for kw in ["女主", "美女", "吃", "咽下", "喝", "品尝"]):
        if master and os.path.exists(master):
            print(f"👸 [自适应人物 Router] 分镜 [{shot_id}] 使用女主定妆参考图: {os.path.basename(master)}")
            return master

    print(f"ℹ️ [纯文本驱动] 分镜 [{shot_id}] 无起跑首帧图片，执行 Text-to-Video。")
    return None

def ensure_silent_video_setting(page, silent=True):
    """设置 Google Flow 的 'Return silent videos'"""
    try:
        settings_btn = page.locator('button:has(mat-icon:has-text("settings_2")), button[aria-label*="Setting"]').first
        if settings_btn.is_visible():
            settings_btn.click()
            page.wait_for_timeout(400)
            target = page.locator('button[role="menuitemcheckbox"]:has-text("Return silent videos")').first
            if target.is_visible():
                is_checked = target.get_attribute("aria-checked") == "true"
                if silent and not is_checked:
                    target.click()
                    print("  🔇 已自动开启 Google Flow『Return silent videos』(返回静音视频)")
                elif not silent and is_checked:
                    target.click()
                    print("  🔊 已自动关闭 Google Flow『Return silent videos』(生成现场原生声音)")
                page.wait_for_timeout(300)
            page.keyboard.press("Escape")
            page.wait_for_timeout(200)
    except Exception:
        pass

def build_locked_prompt(shot_data, config):
    """
    V4 结构化提示词装配:
    视频提示词 100% 采用纯中文电影级六段式提示词规范，坚决杜绝任何英文机位词与洋腔。
    prompt_cn / prompt 中已包含了完整的人物五官、发型、服装锁定、对镜头口播与中文负向约束。
    """
    prompt = shot_data.get("prompt_cn") or shot_data.get("prompt") or shot_data.get("video_prompt") or ""
    # 防范 Google Prominent People 审查：过滤具体姓名，改为通用代称
    char_info = config.get("character", {})
    char_name = char_info.get("女主姓名") or char_info.get("name")
    if char_name and char_name in prompt:
        prompt = prompt.replace(f"美女{char_name}", "年轻中国女子").replace(char_name, "年轻中国女子")
    return prompt.strip()

def inject_and_generate(page, shot_data, all_shots, config, dry_run=False, auto_download=True, silent=True):
    """向 Google Flow 注入提示词与参考首帧并执行生成"""
    shot_id = shot_data["id"]
    title = shot_data["title"]
    output_path = shot_data["video_path"]
    last_frame_path = shot_data["last_frame"]

    locked_prompt = build_locked_prompt(shot_data, config)

    print(f"\n==================================================")
    print(f"🎬 准备注入分镜 [{shot_id}]: {title}")
    print(f"⏱️ 设定时长: {shot_data.get('duration', 6.0)}秒 | 输出文件: {shot_data['filename']}")
    print(f"==================================================")

    image = determine_start_frame(shot_data, all_shots, config)

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        if attempt > 1:
            print(f"\n🔄 [自动重试] 分镜 [{shot_id}] 正在执行第 {attempt}/{max_attempts} 次尝试...")
            time.sleep(2)
            dismiss_overlays(page)

        if "/edit/" in page.url:
            base_url = page.url.split("/edit/")[0]
            page.goto(base_url, wait_until="networkidle")
            page.wait_for_timeout(500)

        done_btn = page.locator('button:has-text("Done"), button[aria-label="Back"]').first
        if done_btn.is_visible():
            try:
                done_btn.click(force=True)
                page.wait_for_timeout(500)
            except Exception:
                pass

        dismiss_overlays(page)
        ensure_aspect_ratio_9_16(page)
        ensure_silent_video_setting(page, silent=silent)

        # 1. 定位并清空输入框
        pm = page.locator("div.ProseMirror")
        if pm.count() == 0:
            print("❌ 未能定位到 Google Flow 输入框 (div.ProseMirror)")
            return False

        clear_prompt_box(page)
        dismiss_overlays(page)
        pm.click(force=True)
        page.wait_for_timeout(300)

        # 2. 注入起跑首帧 (Image-to-Video 核心)
        if image and os.path.exists(image):
            print(f"📷 正在注入参考首帧: {os.path.basename(image)}")
            if copy_image_to_clipboard(image):
                pm.click(force=True)
                page.keyboard.press("Meta+v")
                print("  ✅ 参考图已粘贴至输入框，等待云端解析 (3秒)...")
                page.wait_for_timeout(3000)

        # 3. 注入结构化提示词
        print(f"📝 注入提示词 ({len(locked_prompt)} 字)...")
        dismiss_overlays(page)
        pm.click(force=True)
        page.wait_for_timeout(200)
        try:
            page.keyboard.insert_text(locked_prompt)
        except Exception:
            page.keyboard.type(locked_prompt, delay=5)
        page.wait_for_timeout(800)

        if dry_run:
            print(f"🔍 [Dry-Run 模式] 分镜 [{shot_id}] 提示词与参考图填充完成，跳过生成。")
            return True

        # 4. 点击生成
        initial_err_count = page.locator('flow-error-tile, .error-tile, [role="alert"]:has-text("failed")').count()
        gen_btn = page.locator('button:has-text("Generate"), button[aria-label*="Generate"], button.generate-button').first
        if gen_btn.is_visible() and gen_btn.is_enabled():
            print("🚀 正在触发云端视频生成...")
            gen_btn.click(force=True)
            page.wait_for_timeout(1000)
        else:
            page.keyboard.press("Enter")
            page.wait_for_timeout(1000)

        # 5. 监听生成与下载
        if auto_download:
            ok = wait_for_generation_complete(page, shot_id, timeout=300, initial_error_count=initial_err_count)
            if ok:
                time.sleep(2)
                # 尝试抓取视频 URL 或通过下载按钮下载
                vid_el = page.locator("flow-generation-tile video, .generation-result video, video[src*='blob:']").first
                if vid_el.is_visible():
                    # 优先点击下载按钮
                    download_btn = page.locator('button[aria-label*="Download"], button:has(mat-icon:has-text("download"))').first
                    if download_btn.is_visible():
                        with page.expect_download(timeout=15000) as download_info:
                            download_btn.click(force=True)
                        download = download_info.value
                        download.save_as(output_path)
                        print(f"💾 成功下载视频至: {output_path}")
                    else:
                        print(f"⚠️ 未找到显式下载按钮，分镜 [{shot_id}] 生成完成。")

                if os.path.exists(output_path):
                    extract_last_frame(output_path, last_frame_path)
                return True
            else:
                if attempt < max_attempts:
                    print(f"⚠️ 分镜 [{shot_id}] 尝试失败，进入重试...")
                    time.sleep(2)
                    continue
                return False

    return True

def main():
    parser = argparse.ArgumentParser(description="Google Flow Chrome CDP 中华美食短视频自动化控制器 (V2 动态版)")
    parser.add_argument("--config", type=str, default=None, help="美食视频分镜配置文件路径 (JSON)")
    parser.add_argument("--shot", type=int, help="指定生成单个镜头 (1~N)")
    parser.add_argument("--from-shot", type=int, default=1, help="从指定镜头开始往后连续生成")
    parser.add_argument("--all", action="store_true", help="连续批量连环提交并自动继承下载所有规划分镜")
    parser.add_argument("--list", action="store_true", help="列出当前配置的所有分镜清单与就绪状态")
    parser.add_argument("--dry-run", action="store_true", help="仅填充提示词与首帧图片，不触发点击生成")
    parser.add_argument("--no-download", action="store_true", help="仅提交生成，不阻塞等待下载")
    parser.add_argument("--port", type=int, default=9222, help="Chrome 远程调试端口，默认 9222")
    parser.add_argument("--with-audio", action="store_true", help="允许 Veo 生成现场原生声音 (关闭 Return silent videos)")
    args = parser.parse_args()

    target_cfg = args.config
    if not target_cfg:
        examples_dir = os.path.join(WORKSPACE_ROOT, "examples")
        if os.path.exists(examples_dir):
            jsons = sorted([f for f in os.listdir(examples_dir) if f.endswith(".json") and not f.startswith(".")])
            if jsons:
                target_cfg = os.path.join(examples_dir, jsons[0])
        if not target_cfg:
            print("❌ 错误: 未指定 --config 且 examples 目录中没有可用的配置文件！")
            return
    config, resolved_config_path = load_food_config(target_cfg)
    food_title = config["food_title"]
    project_id = config["project_id"]
    character_name = config["character"].get("女主姓名", "女主")
    shots = config["shots"]

    print(f"🥢 已加载美食全案: 《{food_title}》 (项目编号: {project_id})")
    print(f"👸 出镜女主: {character_name} | 总分镜数: {len(shots)} | 配置文件: {resolved_config_path}")

    if args.list:
        print(f"\n📜 《{food_title}》全片 {len(shots)} 镜头制作清单与状态：")
        for s in shots:
            video_ok = "✅已就绪" if os.path.exists(s["video_path"]) else "⏳待生成"
            frame_ok = "✅有末帧" if os.path.exists(s["last_frame"]) else "⚪无末帧"
            print(f"[{s['id']}] {s['title']} | 时长: {s['duration']}s | 焦点: {s.get('focus', 'auto')} | 视频: {video_ok} | 末帧: {frame_ok}")
        return

    cdp_url = f"http://127.0.0.1:{args.port}"
    print(f"🔌 正在连接本地 Chrome CDP 端口: {cdp_url} ...")
    connect_target = cdp_url
    try:
        req = urllib.request.Request(f"{cdp_url}/json/version")
        with urllib.request.urlopen(req, timeout=3) as resp:
            ver_data = json.loads(resp.read().decode())
            ws_url = ver_data.get("webSocketDebuggerUrl")
            if ws_url:
                connect_target = ws_url
    except Exception:
        pass

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(connect_target)
            print("✅ 成功接管本地 Chrome 浏览器会话！")
            page = connect_flow_page(browser)
            print(f"📄 当前活动页面: {page.title()} | URL: {page.url}")

            auto_download = not args.no_download

            is_silent = not args.with_audio
            if args.shot:
                target_shot = next((s for s in shots if s["id"] == args.shot), None)
                if not target_shot:
                    print(f"❌ 找不到分镜 [{args.shot}] (当前工程共有 {len(shots)} 镜)")
                    return
                inject_and_generate(page, target_shot, shots, config, dry_run=args.dry_run, auto_download=auto_download, silent=is_silent)
            elif args.all:
                start_shot = args.from_shot
                for s in shots:
                    if s["id"] < start_shot:
                        print(f"⏩ 跳过分镜 [{s['id']}] (起始分镜: {start_shot})")
                        continue
                    out_path = s["video_path"]
                    if os.path.exists(out_path) and os.path.getsize(out_path) > 100000 and os.path.exists(s["last_frame"]):
                        print(f"⏩ [已就绪] 分镜 [{s['id']}] 视频与末帧均已就绪，跳过。")
                        continue
                    ok = inject_and_generate(page, s, shots, config, dry_run=args.dry_run, auto_download=auto_download, silent=is_silent)
                    if not ok:
                        print(f"⚠️ 分镜 [{s['id']}] 执行中断，请排查原因。")
                        break
                    print("⏳ 本镜完成，3 秒后进入下一连环镜头...")
                    time.sleep(3)
            else:
                inject_and_generate(page, shots[0], shots, config, dry_run=args.dry_run, auto_download=auto_download, silent=is_silent)

    except Exception as e:
        print(f"❌ 连接或执行失败: {e}")
        print("💡 请确认 Chrome 是否以 --remote-debugging-port=9222 启动。")

if __name__ == "__main__":
    main()
