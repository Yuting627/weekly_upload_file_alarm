# -*- coding: utf-8 -*-
"""Windows 小工具：进程列表、窗口位置、crashpad_handler、隐藏图标面板。"""
import os
import subprocess
import sys


def get_window_rect(title_substring=None, class_name=None):
    """
    获取某个窗口在屏幕上的位置和大小（像素）。
    仅 Windows，使用 ctypes 调用 user32，无需额外依赖。

    :param title_substring: 窗口标题包含的字符串，如 "微信"、"WeChat"；None 表示任意
    :param class_name: 窗口类名，如 "WeChatMainWndForPC"；None 表示任意
    :return: dict 如 {"left": 100, "top": 50, "right": 900, "bottom": 700, "width": 800, "height": 650}
            未找到窗口返回 None
    """
    if sys.platform != "win32":
        return None
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32

        if title_substring or class_name:
            hwnd = _find_window(user32, title_substring, class_name)
        else:
            hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None
        rect = wintypes.RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return None
        return {
            "left": rect.left,
            "top": rect.top,
            "right": rect.right,
            "bottom": rect.bottom,
            "width": rect.right - rect.left,
            "height": rect.bottom - rect.top,
        }
    except Exception:
        return None


def _find_window(user32, title_substring=None, class_name=None):
    """枚举顶层窗口，按标题/类名匹配，返回句柄。"""
    result = [None]

    def enum_cb(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        if class_name:
            buf = ctypes.create_unicode_buffer(256)
            if user32.GetClassNameW(hwnd, buf, 256) and buf.value != class_name:
                return True
        if title_substring:
            buf = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(hwnd, buf, 512)
            if title_substring not in buf.value:
                return True
        result[0] = hwnd
        return False

    try:
        import ctypes
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        return result[0]
    except Exception:
        return None


def list_window_titles():
    """
    列出当前所有可见顶层窗口的标题与类名（便于查要操作的窗口）。
    仅 Windows。
    """
    if sys.platform != "win32":
        return []
    out = []
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        rect = wintypes.RECT()

        def enum_cb(hwnd, _):
            if not user32.IsWindowVisible(hwnd):
                return True
            title_buf = ctypes.create_unicode_buffer(512)
            class_buf = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(hwnd, title_buf, 512)
            user32.GetClassNameW(hwnd, class_buf, 256)
            if not title_buf.value.strip():
                return True
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            out.append({
                "title": title_buf.value,
                "class": class_buf.value,
                "left": rect.left, "top": rect.top,
                "right": rect.right, "bottom": rect.bottom,
            })
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    except Exception:
        pass
    return out


def get_running_process_names():
    """获取当前系统正在运行的程序名称列表。Windows 用 tasklist，其他系统尝试 psutil。"""
    names = []
    try:
        if sys.platform == "win32":
            r = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if r.returncode == 0 and r.stdout:
                for line in r.stdout.strip().splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('"'):
                        end = line.index('"', 1)
                        name = line[1:end].strip()
                    else:
                        name = line.split(",")[0].strip().strip('"')
                    if name and name.upper() != "IMAGE NAME":
                        names.append(name)
        else:
            try:
                import psutil
                for p in psutil.process_iter(["name"]):
                    try:
                        n = p.info.get("name")
                        if n:
                            names.append(n)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except ImportError:
                pass
    except (subprocess.TimeoutExpired, OSError, ValueError):
        pass
    return sorted(set(names))


def find_crashpad_handler_exe():
    """在常见 Chrome/Chromium/Edge 安装目录下查找 crashpad_handler.exe。"""
    if sys.platform != "win32":
        return None
    name = "crashpad_handler.exe"
    search_dirs = []
    for base in (
        os.environ.get("ProgramFiles", "C:\\Program Files"),
        os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
        os.path.expandvars("%LocalAppData%"),
    ):
        if not base:
            continue
        for sub in ["Google\\Chrome\\Application", "Chromium\\Application", "Microsoft\\Edge\\Application"]:
            app_path = os.path.join(base, sub)
            if not os.path.isdir(app_path):
                continue
            try:
                for ver in os.listdir(app_path):
                    p = os.path.join(app_path, ver, name)
                    if os.path.isfile(p):
                        search_dirs.append(p)
            except OSError:
                pass
    return search_dirs[0] if search_dirs else None


def open_crashpad_handler():
    """定位并启动 crashpad_handler.exe。"""
    exe = find_crashpad_handler_exe()
    if not exe:
        print("未找到 crashpad_handler.exe（请确认已安装 Chrome/Chromium/Edge）。")
        return False
    try:
        subprocess.Popen([exe], cwd=os.path.dirname(exe), shell=False)
        print("已启动:", exe)
        return True
    except OSError as e:
        print("启动失败:", e)
        return False


def open_windows_hidden_icons():
    """打开 Windows 任务栏「隐藏图标」面板（Win+B + Enter）。"""
    if sys.platform != "win32":
        print("仅支持 Windows。")
        return False
    try:
        import ctypes
        import time
        VK_LWIN = 0x5B
        VK_RETURN = 0x0D
        KEYEVENTF_KEYUP = 0x0002
        keybd_event = ctypes.windll.user32.keybd_event
        keybd_event(VK_LWIN, 0, 0, 0)
        keybd_event(ord("B"), 0, 0, 0)
        keybd_event(ord("B"), 0, KEYEVENTF_KEYUP, 0)
        keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.25)
        keybd_event(VK_RETURN, 0, 0, 0)
        keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
        print("已发送 Win+B、Enter，应已打开隐藏图标面板。")
        return True
    except Exception as e:
        print("打开隐藏图标面板失败:", e)
        return False
