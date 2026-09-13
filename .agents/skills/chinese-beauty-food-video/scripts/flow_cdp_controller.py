#!/usr/bin/env python3
"""
中华美食短视频 Google Flow (Veo) Chrome CDP + Playwright 通用自动化控制器 (工业升级版)
- 100% 纯中文提示词、日志与分镜驱动
- 复用本地已登录 Google Ultra 账户的 Chrome 浏览器实例 (localhost:9222)
- 黄金3秒美女与美食双爆钩子 + 全片单向递进叙事流
- 全分镜强制锁定女主专属容貌与特定服饰前缀，彻底封杀变脸与换衣服
- 自动设置 9:16 竖屏高画质
- 原生剪贴板毫秒级注入起跑首帧 (Image-to-Video 锚点)
- 实时监听云端渲染进度 (0%~100%) 并精准抓取最新生成的视频下载
- OpenCV 毫秒级提取视频末帧供后续分镜连环继承
"""

import os
import sys
import time
import json
import argparse
import subprocess
import urllib.request
import shutil
import tempfile
import cv2

os.environ["no_proxy"] = "localhost,127.0.0.1,*"
os.environ["NO_PROXY"] = "localhost,127.0.0.1,*"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

from playwright.sync_api import sync_playwright

WORKSPACE_ROOT = "/Users/shuozheng/Documents/meinv"
DEFAULT_CONFIG_PATH = os.path.join(WORKSPACE_ROOT, "examples", "zibo_shaokao_45s.json")
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
    """加载并标准化美食短视频配置文件 (全面兼容纯中文键名)"""
    target_path = resolve_workspace_path(config_path)
    if not os.path.exists(target_path):
        alt_path = os.path.join(WORKSPACE_ROOT, "examples", os.path.basename(config_path))
        if os.path.exists(alt_path):
            target_path = alt_path
        else:
            raise FileNotFoundError(f"未找到美食配置文件: {config_path} (尝试路径: {target_path})")

    with open(target_path, "r", encoding="utf-8") as f:
        raw_config = json.load(f)

    project_id = raw_config.get("项目编号") or raw_config.get("project_id", "food_video")
    food_title = raw_config.get("美食主题") or raw_config.get("food_title", "中华美食")
    character_info = raw_config.get("出镜女主设定") or raw_config.get("character", {})
    master_photo = resolve_workspace_path(
        character_info.get("定妆原图路径") or character_info.get("photo_path", "")
    )

    raw_shots = raw_config.get("分镜列表") or raw_config.get("shots", [])
    normalized_shots = []

    for s in raw_shots:
        shot_id = s.get("镜号") or s.get("id")
        title = s.get("阶段定位") or s.get("title", f"分镜 {shot_id}")
        prompt = s.get("纯中文视频生成提示词") or s.get("prompt", "")
        ref_strategy = s.get("参考帧继承策略") or s.get("reference_strategy", "")
        duration = float(s.get("时长") or s.get("duration", 6.0))
        dialogue = s.get("旁白台词") or s.get("dialogue", "")
        audio_notes = s.get("声音拟音与音乐控制") or s.get("audio_notes", "")

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
            "duration": duration,
            "dialogue": dialogue,
            "audio_notes": audio_notes,
            "filename": filename,
            "video_path": video_path,
            "last_frame": last_frame,
            "initial_image": initial_image,
            "master_photo": master_photo
        })

    config = {
        "project_id": project_id,
        "food_title": food_title,
        "character": character_info,
        "master_photo": master_photo,
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
    clear_btn = page.locator('button[aria-label="Clear prompt"]')
    if clear_btn.is_visible():
        clear_btn.click(force=True)
        page.wait_for_timeout(300)
    else:
        pm.click(force=True)
        page.keyboard.press("Meta+a")
        page.keyboard.press("Backspace")
        page.wait_for_timeout(200)

def wait_and_download_video(page, shot_id, output_path, timeout=360, prev_error_count=0):
    """监听分镜渲染进度，并自动抓取最新生成的视频下载"""
    print(f"⏳ 正在监听分镜 [{shot_id}] 的云端渲染进度 (最长等待: {timeout}秒)...")
    start_time = time.time()
    last_reported_status = ""
    had_progress = False

    while time.time() - start_time < timeout:
        try:
            policy_toast = page.locator('.mat-mdc-snack-bar-container:has-text("violate"), [role="alert"]:has-text("violate")')
            if policy_toast.count() > 0 and policy_toast.first.is_visible():
                print(f"\n❌ 分镜 [{shot_id}] 触发 Google Flow 实时政策拦截: {policy_toast.first.inner_text(timeout=500)}")
                return False
        except Exception:
            pass

        try:
            err_tiles = page.locator('flow-error-tile, .error-tile, [role="alert"]:has-text("failed")')
            if err_tiles.count() > prev_error_count:
                err_text = err_tiles.last.inner_text(timeout=500).strip().replace('\n', ' ')
                print(f"\n❌ 分镜 [{shot_id}] 云端生成遇到偶发故障: {err_text}")
                return False
        except Exception:
            pass

        progress_nodes = page.locator("text=/%/").all()
        current_pct = None
        for pn in progress_nodes:
            try:
                txt = pn.inner_text(timeout=500).strip()
                if "%" in txt and len(txt) <= 6:
                    current_pct = txt
                    had_progress = True
                    if txt != last_reported_status:
                        print(f"  📊 分镜 [{shot_id}] 渲染进度: {txt}")
                        last_reported_status = txt
            except Exception:
                pass

        # 当进度达到 100% 或进度消失后进入下载
        if current_pct == "100%" or (had_progress and not current_pct):
            print(f"\n🎉 分镜 [{shot_id}] 渲染完毕，准备精准获取最新生成的视频...")
            time.sleep(2)
            dismiss_overlays(page)

            # 点击最左上角第一张最新卡片打开全屏详情播放器
            first_tile = page.locator('flow-video-tile, div:has(> img[src*="flow-content"]), div:has(> img[src*="/asb/"])').first
            if first_tile.is_visible():
                try:
                    first_tile.click(force=True)
                    time.sleep(2)
                except Exception:
                    pass

            # 优先从详情播放器的 video 标签提取高清直链
            for v in page.locator("video").all():
                src = v.get_attribute("src")
                if src and src.startswith("http"):
                    print(f"🎉 捕捉到分镜 [{shot_id}] 详情播放器高清直链!")
                    resp = page.request.get(src)
                    if resp.status == 200 and len(resp.body()) > 50000:
                        with open(output_path, "wb") as f:
                            f.write(resp.body())
                        file_mb = len(resp.body()) / (1024 * 1024)
                        print(f"✅ 分镜 [{shot_id}] 视频下载完成！文件大小: {file_mb:.2f} MB")
                        done_btn = page.locator('button:has-text("Done"), button[aria-label="Back"]').first
                        if done_btn.is_visible():
                            done_btn.click()
                        else:
                            page.keyboard.press("Escape")
                        return True

            # 备选：通过详情顶栏的 720p 菜单下载
            temp_dl_dir = tempfile.mkdtemp(prefix=f"flow_dl_{shot_id}_")
            try:
                cdp = page.context.new_cdp_session(page)
                cdp.send("Page.setDownloadBehavior", {
                    "behavior": "allow",
                    "downloadPath": temp_dl_dir
                })
                dl_btn = page.locator('button[aria-label="Download media"], button[aria-label="Download"]').first
                if dl_btn.is_visible():
                    dl_btn.click()
                    time.sleep(0.5)
                    btn_720 = page.locator('.cdk-overlay-container button:has-text("720p"), .cdk-overlay-container [role="menuitem"]:has-text("720p")').first
                    if btn_720.is_visible():
                        btn_720.click()
                        for _ in range(45):
                            time.sleep(1)
                            files = [f for f in os.listdir(temp_dl_dir) if f.endswith(".mp4") and not f.endswith(".crdownload")]
                            if files:
                                downloaded = os.path.join(temp_dl_dir, files[0])
                                if os.path.getsize(downloaded) > 100000:
                                    shutil.move(downloaded, output_path)
                                    print(f"✅ 分镜 [{shot_id}] 视频通过 720p 菜单下载完成！文件大小: {os.path.getsize(output_path)/1024/1024:.2f} MB")
                                    done_btn = page.locator('button:has-text("Done"), button[aria-label="Back"]').first
                                    if done_btn.is_visible():
                                        done_btn.click()
                                    else:
                                        page.keyboard.press("Escape")
                                    return True
            except Exception as e:
                print(f"  ℹ️ 下载通道提示: {e}")
            finally:
                if os.path.exists(temp_dl_dir):
                    shutil.rmtree(temp_dl_dir, ignore_errors=True)
            done_btn = page.locator('button:has-text("Done"), button[aria-label="Back"]').first
            if done_btn.is_visible():
                done_btn.click()
            else:
                page.keyboard.press("Escape")

        time.sleep(3)

    print(f"\n⏰ 分镜 [{shot_id}] 等待渲染超时 ({timeout}秒)")
    return False

def determine_start_frame(shot_data, all_shots, config):
    """
    智能解析分镜的首帧继承逻辑：
    1. 显式指定的 initial_image 拥有最高优先级；
    2. 分镜 1 属于【黄金 3 秒美女首击抓人钩子】，强制使用女主基准定妆原图，确保开场即惊艳；
    3. 分镜 2 优先继承分镜 1 末帧，若无则回溯定妆原图；
    4. 分镜 6 触发【空镜重定向锚定准则 (Re-anchor Rule)】：回溯锁定分镜 1/2 女主末帧，严禁继承分镜 5 的无脸特写；
    5. 其余常规分镜默认继承前序分镜 (N-1) 的最后一帧。
    """
    shot_id = shot_data["id"]
    ref_strategy = shot_data.get("ref_strategy", "")
    explicit_image = shot_data.get("initial_image")

    if explicit_image and os.path.exists(explicit_image):
        print(f"📌 [显式首帧] 分镜 [{shot_id}] 使用显式指定首帧: {os.path.basename(explicit_image)}")
        return explicit_image

    master = config.get("master_photo")

    # 分镜 1：黄金 3 秒美女首击抓人钩子，强制锁定女主专属定妆原图
    if shot_id == 1:
        if master and os.path.exists(master):
            print(f"🌟 [黄金钩子定妆锚定] 分镜 [1] 强锁定女主专属定妆原图: {os.path.basename(master)}")
            return master

    # 分镜 2：优先继承第 1 镜末帧，若不存在则回溯女主定妆照
    if shot_id == 2:
        shot1 = next((s for s in all_shots if s["id"] == 1), None)
        if shot1 and os.path.exists(shot1["last_frame"]):
            print(f"🔗 [连环继承] 分镜 [2] 继承分镜 [1] 咬下后末帧: {os.path.basename(shot1['last_frame'])}")
            return shot1["last_frame"]
        if master and os.path.exists(master):
            print(f"🌟 [女主定妆锚定] 分镜 [2] 回溯锁定女主专属定妆原图: {os.path.basename(master)}")
            return master

    # 分镜 6：【重定向锚定准则 (Re-anchor Rule)】
    if shot_id == 6 or "重定向" in ref_strategy or "回溯" in ref_strategy:
        # 优先回溯到第 1 镜或第 2 镜女主面部末帧
        for candidate_id in [2, 1]:
            cand_shot = next((s for s in all_shots if s["id"] == candidate_id), None)
            if cand_shot and os.path.exists(cand_shot["last_frame"]):
                print(f"🔄 [重定向锚定准则] 分镜 [{shot_id}] 回溯锁定分镜 [{candidate_id}] 女主面部末帧: {os.path.basename(cand_shot['last_frame'])} (规避无脸特写污染)")
                return cand_shot["last_frame"]
        if master and os.path.exists(master):
            print(f"🔄 [重定向锚定准则] 分镜 [{shot_id}] 回溯锁定女主定妆原图: {os.path.basename(master)}")
            return master

    # 常规镜头：继承前一镜头末帧
    prev_shot = next((s for s in all_shots if s["id"] == shot_id - 1), None)
    if prev_shot:
        prev_last_frame = prev_shot["last_frame"]
        if not os.path.exists(prev_last_frame):
            prev_video = prev_shot["video_path"]
            if os.path.exists(prev_video):
                print(f"🔄 检测到前序分镜 [{prev_shot['id']}] 视频已存在，正在提取末帧...")
                extract_last_frame(prev_video, prev_last_frame)
            else:
                print(f"❌ 前序分镜 [{prev_shot['id']}] 尚未生成，无法连环继承！")
                return None
        if os.path.exists(prev_last_frame):
            print(f"🔗 [连环继承] 分镜 [{shot_id}] 继承前一镜 [{prev_shot['id']}] 末帧: {os.path.basename(prev_last_frame)}")
            return prev_last_frame

    return None

def build_locked_prompt(shot_data, config):
    """确保提示词中强制注入女主完整外貌与特定衣着前缀，封杀变脸与换衣服"""
    base_prompt = shot_data["prompt"]
    character_info = config["character"]
    character_name = character_info.get("女主姓名", "女主")
    visual_traits = character_info.get("身材与面貌特征") or character_info.get("visual_traits", "")

    # 检查是否已包含强制锁定前缀
    if "【锁定出镜人物】" not in base_prompt and "【锁定女主】" not in base_prompt:
        # 仅对人物相关分镜注入（非纯食材微距镜头）
        if any(kw in base_prompt for kw in [character_name, "美女", "双手", "吃", "咽下", "喝", "直视", "眼神"]):
            prefix = f"【锁定出镜人物】：20岁中国美女{character_name}，{visual_traits}。全片严格保持同一人，严禁变脸，严禁更换衣服。"
            base_prompt = f"{prefix} {base_prompt}"

    # 统一附带严苛负向约束后置拦截
    neg_block = " 严禁更换衣服，严禁白衬衫，严禁散发，严禁长直发，严禁头顶光环，严禁胸前麦克风，严禁变脸，严禁塑料假脸。"
    if "严禁更换衣服" not in base_prompt:
        base_prompt += neg_block

    return base_prompt

def inject_and_generate(page, shot_data, all_shots, config, dry_run=False, auto_download=True):
    """向 Google Flow 注入提示词与参考首帧并执行生成"""
    shot_id = shot_data["id"]
    title = shot_data["title"]
    output_path = shot_data["video_path"]
    last_frame_path = shot_data["last_frame"]

    # 构建锁定外貌与服饰的终极纯中文提示词
    locked_prompt = build_locked_prompt(shot_data, config)

    print(f"\n==================================================")
    print(f"🎬 准备注入分镜 [{shot_id}]: {title}")
    print(f"⏱️ 设定时长: {shot_data.get('duration', 6.0)}秒 | 输出文件: {shot_data['filename']}")
    print(f"==================================================")

    image = determine_start_frame(shot_data, all_shots, config)

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        if attempt > 1:
            print(f"\n🔄 [自动重试机制] 分镜 [{shot_id}] 正在执行第 {attempt}/{max_attempts} 次重试...")
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
        prev_error_count = page.locator('flow-error-tile, .error-tile, [role="alert"]:has-text("failed")').count()

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
            print(f"📷 正在强注入起跑首帧 (Image-to-Video 锚点): {os.path.basename(image)}")
            if copy_image_to_clipboard(image):
                pm.click(force=True)
                page.keyboard.press("Meta+v")
                print("  ✅ 首帧已粘贴至提示词框，等待云端解析 (3秒)...")
                page.wait_for_timeout(3000)
        else:
            print(f"ℹ️ 分镜 [{shot_id}] 无起跑首帧图片，执行 Text-to-Video。")

        # 3. 注入纯中文 Prompt
        print(f"📝 正在注入锁定外貌与服饰的纯中文连续运镜提示词 ({len(locked_prompt)} 字)...")
        dismiss_overlays(page)
        pm.click(force=True)
        page.keyboard.type(locked_prompt, delay=5)
        page.wait_for_timeout(1000)
        print("  ✅ 提示词注入完成！")

        if dry_run:
            print("🔍 [Dry-Run 预览模式] 不触发实际点击生成按钮。")
            return True

        # 4. 点击生成按钮
        gen_btn = page.locator('button[aria-label="Start generation"], button.generate-icon-button, button:has(mat-icon:has-text("arrow_forward"))').last
        if gen_btn.is_visible() and gen_btn.is_enabled():
            print("🚀 点击生成按钮 (Start generation)...")
            gen_btn.click(force=True)
            print(f"  🎉 分镜 [{shot_id}] 已成功提交至 Google Flow 云端渲染！")
            page.wait_for_timeout(3000)
        else:
            print("⚠️ 生成按钮当前不可用，请检查页面状态。")
            if attempt < max_attempts:
                continue
            return False

        # 5. 监听下载并提取最后一帧
        if auto_download:
            ok = wait_and_download_video(page, shot_id, output_path, prev_error_count=prev_error_count)
            if ok:
                extract_last_frame(output_path, last_frame_path)
                if "/edit/" in page.url:
                    base_url = page.url.split("/edit/")[0]
                    page.goto(base_url, wait_until="networkidle")
                return True
            else:
                if attempt < max_attempts:
                    print(f"⚠️ 分镜 [{shot_id}] 本次尝试未成功，2秒后自动进入重试...")
                    time.sleep(2)
                    continue
                return False
        return True

def main():
    parser = argparse.ArgumentParser(description="Google Flow Chrome CDP 中华美食短视频自动化控制器")
    parser.add_argument("--config", type=str, default=DEFAULT_CONFIG_PATH, help="美食视频分镜配置文件路径 (JSON)")
    parser.add_argument("--shot", type=int, help="指定生成单个镜头 (1-8)")
    parser.add_argument("--from-shot", type=int, default=1, help="从指定镜头开始往后连续生成")
    parser.add_argument("--all", action="store_true", help="连续批量连环提交并自动继承下载所有分镜")
    parser.add_argument("--list", action="store_true", help="列出当前配置的所有分镜清单与就绪状态")
    parser.add_argument("--dry-run", action="store_true", help="仅填充提示词与首帧图片，不触发点击生成")
    parser.add_argument("--no-download", action="store_true", help="仅提交生成，不阻塞等待下载")
    parser.add_argument("--port", type=int, default=9222, help="Chrome 远程调试端口，默认 9222")
    args = parser.parse_args()

    config, resolved_config_path = load_food_config(args.config)
    food_title = config["food_title"]
    project_id = config["project_id"]
    character_name = config["character"].get("女主姓名", "女主")
    shots = config["shots"]

    print(f"🥢 已加载美食全案: 《{food_title}》 (项目编号: {project_id})")
    print(f"👸 出镜女主: {character_name} | 配置文件: {resolved_config_path}")

    if args.list:
        print(f"\n📜 《{food_title}》全片 {len(shots)} 镜头制作清单与状态：")
        for s in shots:
            video_ok = "✅已就绪" if os.path.exists(s["video_path"]) else "⏳待生成"
            frame_ok = "✅有末帧" if os.path.exists(s["last_frame"]) else "⚪无末帧"
            print(f"[{s['id']}] {s['title']} | 时长: {s['duration']}s | 视频: {video_ok} | 末帧: {frame_ok}")
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

            if args.shot:
                target_shot = next((s for s in shots if s["id"] == args.shot), None)
                if not target_shot:
                    print(f"❌ 找不到分镜 [{args.shot}]")
                    return
                inject_and_generate(page, target_shot, shots, config, dry_run=args.dry_run, auto_download=auto_download)
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
                    ok = inject_and_generate(page, s, shots, config, dry_run=args.dry_run, auto_download=auto_download)
                    if not ok:
                        print(f"⚠️ 分镜 [{s['id']}] 连环中断，请排查原因。")
                        break
                    print("⏳ 本镜完成，3 秒后进入下一连环镜头...")
                    time.sleep(3)
            else:
                inject_and_generate(page, shots[0], shots, config, dry_run=args.dry_run, auto_download=auto_download)

    except Exception as e:
        print(f"❌ 连接或执行失败: {e}")
        print("💡 请确认 Chrome 是否以 --remote-debugging-port=9222 启动。")

if __name__ == "__main__":
    main()
