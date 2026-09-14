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

def activate_chrome():
    subprocess.run(['osascript', '-e', '''
tell application "Google Chrome"
    activate
    set w to first window whose id is 1083145396
    set index of w to 1
    set active tab index of w to 28
end tell
'''], check=True)

print("Helper ready")
