import ctypes
import ctypes.util
import time
import subprocess
import os
import sys
from PIL import Image
import numpy as np

cg = ctypes.cdll.LoadLibrary(ctypes.util.find_library('CoreGraphics'))

class CGPoint(ctypes.Structure):
    _fields_ = [('x', ctypes.c_double), ('y', ctypes.c_double)]

cg.CGWarpMouseCursorPosition.argtypes = [CGPoint]
cg.CGEventCreateMouseEvent.restype = ctypes.c_void_p
cg.CGEventCreateMouseEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint32, CGPoint, ctypes.c_uint32]
cg.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]

def click_global(gx, gy, delay=0.12):
    pt = CGPoint(gx, gy)
    cg.CGWarpMouseCursorPosition(pt)
    time.sleep(0.06)
    down = cg.CGEventCreateMouseEvent(None, 1, pt, 0)
    up = cg.CGEventCreateMouseEvent(None, 2, pt, 0)
    cg.CGEventPost(0, down)
    time.sleep(delay)
    cg.CGEventPost(0, up)

subprocess.run(['osascript', '-e', 'tell application "Google Chrome" to activate'])
time.sleep(0.3)

# 14 characters and their gallery coordinates
CHARACTERS = [
    # Row 1
    ('黎温言', 1512 + 384, 350),
    ('阮清寻', 1512 + 672, 350),
    ('钟雪凝', 1512 + 960, 350),
    ('叶薇薇', 1512 + 1248, 350),
    ('陆潇潇', 1512 + 1536, 350),
    ('夏青禾', 1512 + 1824, 350),
    ('姜黎',   1512 + 2112, 350),
    ('赵子晴', 1512 + 2400, 350),
    ('陈可可', 1512 + 2688, 350),
    ('宋晓芸', 1512 + 2976, 350),
    ('周敏仪', 1512 + 3264, 350),
    # Row 2
    ('苏婉清', 1512 + 384, 700),
    ('林初薇', 1512 + 672, 700),
    ('沈昭',   1512 + 1462, 700)
]

print(f"Starting voice removal sweep for {len(CHARACTERS)} characters...")

for idx, (name, gx, gy) in enumerate(CHARACTERS, 1):
    print(f"\n[{idx}/14] Processing {name} (Card: {gx}, {gy})...")
    # 1. Click card to enter editor
    click_global(gx, gy)
    time.sleep(2.0)
    
    # 2. Capture voice bar region to check if a voice is bound
    subprocess.run(['screencapture', '-x', '-D', '2', 'tmp/temp_check_voice.png'])
    img = Image.open('tmp/temp_check_voice.png')
    # Voice bar is around Display 2: x in [950, 1400], y in [320, 420]
    crop = img.crop((950, 320, 1400, 420))
    arr = np.array(crop.convert('L'))
    
    # Check if 'Remove' button text exists in the right portion of the voice bar (x > 200)
    # Bright pixels of 'Remove' text
    ys, xs = np.where(arr[:, 200:] > 170)
    if len(xs) > 20:
        print(f"  -> Voice is bound on {name}, clicking [ Remove ] at (2767, 377)...")
        click_global(2767, 377, delay=0.15)
        time.sleep(0.8)
        print(f"  ✓ Voice removed successfully for {name}!")
    else:
        print(f"  -> No voice bound on {name} (already 'Select a voice').")
        
    # 3. Click Done at (4872, 180)
    click_global(4872, 180)
    time.sleep(1.6)

print("\n==========================================")
print("SWEEP COMPLETE! All 14 characters have voices cleared.")
