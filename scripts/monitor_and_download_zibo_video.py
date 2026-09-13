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

def click_global(gx, gy, delay=0.1):
    pt = CGPoint(gx, gy)
    cg.CGWarpMouseCursorPosition(pt)
    time.sleep(0.05)
    down = cg.CGEventCreateMouseEvent(None, 1, pt, 0)
    up = cg.CGEventCreateMouseEvent(None, 2, pt, 0)
    cg.CGEventPost(0, down)
    time.sleep(delay)
    cg.CGEventPost(0, up)

def is_video_ready():
    subprocess.run(['screencapture', '-x', '-D', '2', 'tmp/monitor_screen.png'], check=True)
    img = Image.open('tmp/monitor_screen.png')
    # Card 1 is roughly at x: 200 to 580, y: 180 to 450
    card1 = img.crop((220, 200, 560, 420))
    arr = np.array(card1)[:, :, :3]
    std = arr.std()
    print(f"Card 1 color standard deviation: {std:.2f}")
    return std > 30.0, card1

print("Monitoring Veo generation in Google Flow...")
max_wait_seconds = 300
start_time = time.time()

ready = False
while time.time() - start_time < max_wait_seconds:
    ready, card_img = is_video_ready()
    if ready:
        print("Video generation finished!")
        card_img.save('tmp/generated_video_thumb.png')
        break
    print(f"Still generating... elapsed: {int(time.time() - start_time)}s. Waiting 15s...")
    time.sleep(15)

if not ready:
    print("Timed out waiting for generation.")
    sys.exit(1)

subprocess.run(['screencapture', '-x', '-D', '2', 'tmp/generated_screen.png'])
img = Image.open('tmp/generated_screen.png')
img.crop((0, 100, 3440, 800)).resize((1720, 350)).save('tmp/generated_gallery_crop.png')
print("Gallery captured.")
