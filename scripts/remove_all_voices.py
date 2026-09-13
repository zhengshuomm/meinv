import ctypes
import ctypes.util
import time
import subprocess
import sys

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
    time.sleep(0.05)
    down = cg.CGEventCreateMouseEvent(None, 1, pt, 0)
    up = cg.CGEventCreateMouseEvent(None, 2, pt, 0)
    cg.CGEventPost(0, down)
    time.sleep(delay)
    cg.CGEventPost(0, up)

# Activate Chrome
subprocess.run(['osascript', '-e', 'tell application "Google Chrome" to activate'])
time.sleep(0.3)

# All character cards to process
cards = [
    # Row 1 (y=350 on Display 2 -> Global y=350)
    ('黎温言', 1512 + 384, 350),
    ('阮清寻', 1512 + 673, 350),
    ('钟雪凝', 1512 + 961, 350),
    ('叶薇薇', 1512 + 1250, 350),
    ('陆潇潇', 1512 + 1538, 350),
    ('夏青禾', 1512 + 1826, 350),
    ('姜黎',   1512 + 2114, 350),
    ('赵子晴', 1512 + 2402, 350),
    ('陈可可', 1512 + 2690, 350),
    ('宋晓芸', 1512 + 2978, 350),
    ('周敏仪', 1512 + 3266, 350),
    # Row 2 (y=700 on Display 2 -> Global y=700)
    ('苏婉清', 1512 + 384, 700),
    ('林初薇', 1512 + 673, 700),
    ('沈昭',   1512 + 1462, 700)
]

print(f"Starting voice removal for {len(cards)} characters...")

for idx, (name, cx, cy) in enumerate(cards, 1):
    print(f"\n[{idx}/14] Processing {name} (Card at {cx}, {cy})...")
    # 1. Click card in gallery
    click_global(cx, cy)
    time.sleep(1.8)
    
    # 2. Click Remove button at (2767, 377)
    print(f"  -> Clicking [ Remove ] button at (2767, 377)...")
    click_global(2767, 377, delay=0.15)
    time.sleep(0.8)
    
    # 3. Click back arrow at (1536, 158)
    print(f"  -> Returning to gallery...")
    click_global(1536, 158)
    time.sleep(1.5)
    print(f"  ✓ {name} voice removed!")

print("\n==========================================")
print("ALL 14 CHARACTERS PROCESSED!")
print("Capturing final verification screenshot...")
subprocess.run(['screencapture', '-x', '-D', '2', 'tmp/all_voices_removed_gallery.png'])
print("Done!")
