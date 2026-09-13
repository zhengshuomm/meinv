import ctypes
import ctypes.util
import time
import subprocess
import os
import sys

cg = ctypes.cdll.LoadLibrary(ctypes.util.find_library('CoreGraphics'))

class CGPoint(ctypes.Structure):
    _fields_ = [('x', ctypes.c_double), ('y', ctypes.c_double)]

cg.CGWarpMouseCursorPosition.argtypes = [CGPoint]
cg.CGEventCreateMouseEvent.restype = ctypes.c_void_p
cg.CGEventCreateMouseEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint32, CGPoint, ctypes.c_uint32]
cg.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]

def click_global(gx, gy, delay=0.08):
    pt = CGPoint(gx, gy)
    cg.CGWarpMouseCursorPosition(pt)
    time.sleep(0.05)
    down = cg.CGEventCreateMouseEvent(None, 1, pt, 0)
    up = cg.CGEventCreateMouseEvent(None, 2, pt, 0)
    cg.CGEventPost(0, down)
    time.sleep(delay)
    cg.CGEventPost(0, up)

def run_osa(script):
    subprocess.run(['osascript', '-e', script], check=True)

VOICE_COORDS = {
    'Achernar': (2932, 585),
    'Aoede': (2932, 856),
    'Autonoe': (2932, 910),
    'Callirrhoe': (2932, 964),
    'Despina': (2932, 1072)
}

CHARACTERS_TO_UPLOAD = [
    {
        'index': 3,
        'name': '苏婉清',
        'photo_path': '/Users/shuozheng/Documents/meinv/assets/character_master/girl_guofeng_beauty_1789285173133.jpg',
        'voice': 'Achernar',
        'info': '20岁中国美女苏婉清，温润冷白皮，远山秋水眉，优雅丹凤眼，传统低挽发髻别雅致银花簪。身穿淡竹青提花真丝高开叉旗袍配浅裸色细高跟鞋，天鹅颈，步态轻盈端庄，长腿线条曼妙修长，江南水乡温婉气韵。性格温婉恬静、知书达礼、深谙传统饮食文化与烹饪美学，骨子里透着文人的雅致与从容。出口成章，擅长用充满诗意的语言解构食材时令与匠人火候。'
    },
    {
        'index': 4,
        'name': '周敏仪',
        'photo_path': '/Users/shuozheng/Documents/meinv/assets/character_master/girl_hongkong_retro_1789283316432.jpg',
        'voice': 'Despina',
        'info': '20岁中国美女周敏仪，浓颜系骨相，浓密蓬松的黑色大波浪长卷发，野生浓眉，复古哑光正红唇，冷白皮。身穿复古正红色高开叉真丝吊带长裙配黑色细带高跟鞋与复古金属大耳环，身材曼妙高挑，气场全开。慵懒风情、霸气独立、吃遍大排档与老字号的港岛千金，眼神深邃微醺，既能优雅端坐高级酒楼，也能在大排档大快朵颐。带着王家卫电影般的叙事调性与懂吃讲究。'
    },
    {
        'index': 5,
        'name': '宋晓芸',
        'photo_path': '/Users/shuozheng/Documents/meinv/assets/character_master/girl_literary_gentle_1789283538436.jpg',
        'voice': 'Callirrhoe',
        'info': '20岁中国美女宋晓芸，清透水嫩皮肤，柔和含笑的双眸，细金丝圆框眼镜，松散慵懒的低丸子头。身穿宽松燕麦棉麻浅色衬衫配墨绿百褶棉麻长裙与深棕色乐福鞋，书卷气浓郁，文艺松弛。性格内敛从容、温柔治愈、喜欢探寻食物背后的人情冷暖与市井故事，像一位博学温和的知己闺蜜。娓娓道来，重在情感共鸣与风土人情。'
    },
    {
        'index': 6,
        'name': '陈可可',
        'photo_path': '/Users/shuozheng/Documents/meinv/assets/character_master/girl_playful_cat_1789284992565.jpg',
        'voice': 'Autonoe',
        'info': '20岁中国美女陈可可，饱满心形幼态脸，微挑娇憨猫眼，水润嘟嘟唇，白瓷透光肌，毛茸茸黑棕色微卷发扎着俏皮双半丸子头。身穿浅粉色小香风粗花呢短外套配高腰百褶短裙与黑色玛丽珍鞋，修长纤细双腿，贵气灵动。娇憨傲娇、嘴硬心软、挑食但极懂顶级品质，被好吃的美食征服后会立刻露出又惊又喜的小猫本性。先挑刺后彻底沦陷，反差喜感极强。'
    },
    {
        'index': 7,
        'name': '赵子晴',
        'photo_path': '/Users/shuozheng/Documents/meinv/assets/character_master/girl_sichuan_spicy_1789284409933.jpg',
        'voice': 'Aoede',
        'info': '20岁中国美女赵子晴，白里透红的健康透亮皮肤，灵动狡黠的大眼睛，笑起来带迷人梨涡与虎牙，随性高扎丸子头碎发飞扬。身穿火红短T恤配高腰破洞牛仔超短裤与红白帆布鞋，紧实笔直大长腿，活力爆棚。豪爽开朗、耿直泼辣、自来熟、市井气十足，坐在塑料矮凳上烫火锅手速飞快，江湖气满满。直白火辣、通透接地气、大开大合。'
    },
    {
        'index': 8,
        'name': '姜黎',
        'photo_path': '/Users/shuozheng/Documents/meinv/assets/character_master/girl_sporty_street_1789283379567.jpg',
        'voice': 'Autonoe',
        'info': '20岁中国美女姜黎，阳光健康微光泽冷白皮，高束运动编发马尾，灵动自信目光，清晰紧致马甲线。身穿白色运动挂脖短背心配军绿色高腰工装长裤与复古运动鞋，身材健美高挑，长腿线条力量感十足。直率飒爽、阳光开朗、热爱大排档和路边摊的硬核食客，大口吃肉大口喝酒，毫不扭捏做作。痛快爽快、直击灵魂、肉食主义。'
    },
    {
        'index': 9,
        'name': '夏青禾',
        'photo_path': '/Users/shuozheng/Documents/meinv/assets/character_master/girl_mori_oxygen_1789284502852.jpg',
        'voice': 'Achernar',
        'info': '20岁中国美女夏青禾，白皙近乎透明的发光肌肤，清澈纯净小鹿眼，微卷蓬松栗色碎发。身穿宽松浅燕麦色粗线毛衣外搭白色碎花棉麻长裙与复古小皮靴，体态轻盈柔美，宛如晨雾中走出的林间仙子。纯净出尘、安静平和、对食材本原的味道极其敏感，能够捕捉最细微的甘甜与温度，抚慰人心。感官细腻、温暖抚慰、重在体悟。'
    },
    {
        'index': 10,
        'name': '陆潇潇',
        'photo_path': '/Users/shuozheng/Documents/meinv/assets/character_master/girl_cyber_guochao_1789284794883.jpg',
        'voice': 'Despina',
        'info': '20岁中国美女陆潇潇，轮廓立体分明的瓜子脸，冷酷微挑烟熏猫眼，暗紫色挑染黑色高马尾。身穿黑色战术机能短马甲叠穿紧身网纱与高腰工装百褶短裙，脚蹬及膝厚底系带战靴配网袜，身材修长高挑，冷艳拽酷。特立独行、桀骜不驯、专挑最狠最重口的美食打卡，天不怕地不怕，眼神里全是狂放不羁。狠辣直接、硬核机能、绝不废话。'
    },
    {
        'index': 11,
        'name': '叶薇薇',
        'photo_path': '/Users/shuozheng/Documents/meinv/assets/character_master/night_glam_portrait_1789284995394.jpg',
        'voice': 'Despina',
        'info': '20岁中国美女叶薇薇，冷白皮光泽诱人，精致锁骨与天鹅颈，乌黑微卷披肩发。身穿翡翠墨绿丝绸露肩挂脖吊带裙配细高跟鞋，修长大长腿与曼妙比例，夜景灯火阑珊，纯欲撩人。微醺迷人、优雅自信、懂吃懂喝的生活家，带有一丝小性感但谈起美食来专业犀利。慵懒撩人、品味卓绝，充满夜色诱惑力。'
    },
    {
        'index': 12,
        'name': '钟雪凝',
        'photo_path': '/Users/shuozheng/Documents/meinv/assets/character_master/yujie_beauty_portrait_1789284889424.jpg',
        'voice': 'Callirrhoe',
        'info': '20岁中国美女钟雪凝，冷白皮，身材高挑173cm沙漏型超模曲线，黑色深V长袖修身及膝针织裙，佩戴简约钻石细锁骨链与单颗珍珠耳坠，一头乌黑顺直的长发自然垂落至胸前，五官立体明艳，神态高贵从容，手持精致黑色皮革晚宴包，尽显顶级私享名媛气场。奢雅高贵、从容端庄、品味极致苛刻、深谙高端食材产地与烹饪火候。行云流水的高阶品评、剖析食材细微矿物质感与油脂熟度。'
    },
    {
        'index': 13,
        'name': '阮清寻',
        'photo_path': '/Users/shuozheng/Documents/meinv/assets/character_master/sweet_beauty_portrait_1789284409225.jpg',
        'voice': 'Aoede',
        'info': '20岁中国美女阮清寻，暖白皮透亮，169cm高挑匀称身材，浅米色细罗纹大圆领七分袖针织衫配深灰色高腰西装阔腿裤，单肩斜挎棕色小皮包，阳光下栗黑色半扎微卷发，眉眼弯弯笑容明媚灿烂，带有迷人的梨涡，自然干练又极具亲和力的都市独立女性探店博主形象。明朗爽快、元气积极、极具感染力、喜欢穿梭在城市街头巷尾寻找最真实的人情味与烟火滋味。'
    },
    {
        'index': 14,
        'name': '黎温言',
        'photo_path': '/Users/shuozheng/Documents/meinv/assets/character_master/pure_allure_portrait_1789284977749.jpg',
        'voice': 'Achernar',
        'info': '20岁中国美女黎温言，细腻瓷白皮，170cm纤细曼妙身段，身穿香槟金极简真丝V领吊带长裙，慵懒蜷坐在落地窗边的浅色单人沙发椅上，自然黑褐色中长微卷发微拂肩头，五官清秀纯欲，眼神柔和清澈带有一丝慵懒迷离，晨光洒在光洁的锁骨与肩颈线条上，呈现出高级慵懒的私享品味。慵懒随性、细腻敏感、追求极简纯粹的感官享受、注重食材本味与生活仪式感。'
    }
]

def upload_character(char):
    idx = char['index']
    name = char['name']
    path = char['photo_path']
    voice = char['voice']
    info = char['info']
    
    print(f"\n==========================================")
    print(f"[{idx}/14] Starting creation for: {name} (Voice: {voice})")
    print(f"==========================================")
    
    # 0. Ensure Chrome is active and dismiss any stray overlays
    subprocess.run(['osascript', '-e', 'tell application "Google Chrome" to activate'])
    time.sleep(0.3)
    subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 53'])
    time.sleep(0.3)
    
    # 1. Click '+' at top right
    print(f"  [1] Clicking '+' icon at (4630, 161)...")
    click_global(4630, 161)
    time.sleep(0.7)
    
    # 2. Click 'Create character'
    print(f"  [2] Clicking 'Create character' at (4722, 288)...")
    click_global(4722, 288)
    time.sleep(2.5)
    
    # 3. Click '[ ↑ Upload ]' button
    print(f"  [3] Clicking '[Upload]' button at (3092, 1404)...")
    click_global(3092, 1404)
    time.sleep(1.3)
    
    # 4. Open 'Go to Folder' drawer
    print(f"  [4] Sending Cmd+Shift+G...")
    run_osa('''
tell application "System Events"
    keystroke "g" using {command down, shift down}
end tell
''')
    time.sleep(0.9)
    
    # 5. Paste path and press Enter twice
    print(f"  [5] Pasting photo path: {os.path.basename(path)}...")
    run_osa(f'''
set the clipboard to "{path}"
tell application "System Events"
    delay 0.1
    keystroke "v" using {{command down}}
    delay 0.4
    key code 36
    delay 0.8
    key code 36
end tell
''')
    
    # 6. Wait for photo upload to process and editor UI to appear
    print(f"  [6] Waiting 5.5s for photo upload and editor...")
    time.sleep(5.5)
    
    # 7. Edit Name
    print(f"  [7] Setting Character Name to '{name}'...")
    click_global(2816, 308)
    time.sleep(0.4)
    run_osa(f'''
set the clipboard to "{name}"
tell application "System Events"
    keystroke "a" using {{command down}}
    delay 0.1
    keystroke "v" using {{command down}}
    delay 0.2
    key code 36
end tell
''')
    time.sleep(0.5)
    
    # 8. Open Voice Modal
    print(f"  [8] Opening Voice selection modal at (2648, 365)...")
    click_global(2648, 365)
    time.sleep(1.3)
    
    # 9. Click Voice
    vx, vy = VOICE_COORDS[voice]
    print(f"  [9] Selecting voice '{voice}' at ({vx}, {vy})...")
    click_global(vx, vy)
    time.sleep(0.5)
    
    # 10. Click [Add to character]
    print(f"  [10] Clicking '[Add to character]' at (3354, 1032)...")
    click_global(3354, 1032)
    time.sleep(1.0)
    
    # 11. Click Character info textarea and paste
    print(f"  [11] Pasting Character info...")
    click_global(2652, 500)
    time.sleep(0.4)
    run_osa(f'''
set the clipboard to "{info}"
tell application "System Events"
    keystroke "a" using {{command down}}
    delay 0.1
    keystroke "v" using {{command down}}
end tell
''')
    time.sleep(1.0)
    
    # 12. Save screenshot of verified editor state
    shot_path = f"tmp/char_{idx}_{name}_editor.png"
    subprocess.run(['screencapture', '-x', '-D', '2', shot_path])
    print(f"  [12] Captured verification snapshot: {shot_path}")
    
    # 13. Return to project gallery
    print(f"  [13] Returning to project gallery at (1536, 158)...")
    click_global(1536, 158)
    time.sleep(2.5)
    print(f"  >>> Character {name} completed successfully!")

if __name__ == '__main__':
    start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    for char in CHARACTERS_TO_UPLOAD:
        if char['index'] >= start_idx:
            upload_character(char)
            time.sleep(1.0)
    
    print("\n==========================================")
    print("ALL CHARACTERS SUCCESSFULLY PROCESSED!")
    print("Capturing final gallery verification screenshot...")
    subprocess.run(['screencapture', '-x', '-D', '2', 'tmp/all_14_characters_verified.png'])
    print("Done!")
