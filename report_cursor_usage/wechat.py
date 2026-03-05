# -*- coding: utf-8 -*-
"""微信相关：打开微信、剪贴板、自动发送到指定联系人。"""
import os
import random
import subprocess
import sys

# 微信主窗口内可点击区域 (x_min, x_max, y_min, y_max)，每次在范围内随机选点
# 来源：debug_wechat_chat_position.py 测得 [2]-[4]搜索框 / [5]-[8]输入框 / [10]-[11]发送键
WECHAT_SEARCH_BOX_RANGE = (817, 945, 245, 252)   # 搜索框 [2]-[4]
WECHAT_INPUT_BOX_RANGE = (1037, 1822, 642, 823)  # 输入框 [5]-[8]
WECHAT_SEND_BTN_RANGE = (1735, 1833, 860, 864)   # 发送键 [10]-[11]

WECHAT_PATHS = [
    r"C:\Program Files\Tencent\WeChat\WeChat.exe",
    r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
    os.path.expandvars(r"%ProgramFiles%\Tencent\WeChat\WeChat.exe"),
    os.path.expandvars(r"%ProgramFiles(x86)%\Tencent\WeChat\WeChat.exe"),
]


def _random_point_in_range(x_min, x_max, y_min, y_max):
    """在矩形范围 (x_min~x_max, y_min~y_max) 内随机取一点 (x, y)。"""
    return (random.randint(x_min, x_max), random.randint(y_min, y_max))


def set_clipboard(text):
    """将文本写入系统剪贴板。"""
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QMimeData
        app = QApplication.instance() or QApplication(sys.argv)
        mime = QMimeData()
        mime.setText(text)
        app.clipboard().setMimeData(mime)
        return True
    except Exception:
        pass
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        pass
    return False


def _clipboard_set_pyperclip(text):
    """使用 pyperclip 设置剪贴板（便于中文与特殊字符）。"""
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def _clipboard_get_pyperclip():
    """使用 pyperclip 读取剪贴板。"""
    try:
        import pyperclip
        return pyperclip.paste()
    except Exception:
        return ""


def find_wechat_exe():
    for path in WECHAT_PATHS:
        if path and os.path.isfile(path):
            return path
    return None


def _click_wechat_taskbar_icon():
    """
    点击 Windows 底部任务栏中的微信图标：先定位图标位置，再控制鼠标移动并点击。
    优先用 pywinauto 找到标题为 Weixin/微信 的按钮并取其矩形中心，用 pyautogui 点击；
    若未找到则用图标图像在任务栏区域做图像匹配并点击。
    返回 True 表示成功点击，False 表示未找到或依赖缺失。
    """
    if sys.platform != "win32":
        return False

    def _click_at_rect(rect):
        """根据矩形用 pyautogui 移动鼠标并点击中心。"""
        try:
            import pyautogui
            cx = (rect.left + rect.right) // 2
            cy = (rect.top + rect.bottom) // 2
            pyautogui.moveTo(cx, cy, duration=0.15)
            pyautogui.click(cx, cy)
            return True
        except Exception:
            return False

    # 1) 用 pywinauto 找到任务栏中微信按钮，取矩形后用鼠标点击
    try:
        from pywinauto import Application
        app = Application(backend="uia").connect(path="explorer.exe")
        taskbar = app.window(class_name="Shell_TrayWnd")
        for name in ("微信", "Weixin", "WeChat", "WeChat.exe"):
            try:
                btn = taskbar.child_window(title=name, control_type="Button")
                if btn.exists(timeout=0):
                    rect = btn.rectangle()
                    if _click_at_rect(rect):
                        return True
            except Exception:
                continue
        for desc in taskbar.descendants(control_type="Button"):
            try:
                t = ""
                if hasattr(desc, "window_text"):
                    w = desc.window_text
                    t = w() if callable(w) else (w or "")
                if not t and getattr(desc, "element_info", None):
                    t = getattr(desc.element_info, "name", "") or ""
                if "微信" in t or "WeChat" in t or "Weixin" in t:
                    rect = desc.rectangle()
                    if _click_at_rect(rect):
                        return True
            except Exception:
                continue
    except ImportError:
        pass
    except Exception:
        pass

    # 2) 备用：用图标图像在屏幕底部任务栏区域查找并点击
    try:
        import pyautogui
        _icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wechat_taskbar_icon.png")
        if os.path.isfile(_icon):
            screen_w, screen_h = pyautogui.size()
            region = (0, max(0, screen_h - 80), screen_w, 80)
            try:
                loc = pyautogui.locateOnScreen(_icon, region=region, confidence=0.8)
            except TypeError:
                loc = pyautogui.locateOnScreen(_icon, region=region)
            if loc:
                cx = loc.left + loc.width // 2
                cy = loc.top + loc.height // 2
                pyautogui.moveTo(cx, cy, duration=0.15)
                pyautogui.click(cx, cy)
                return True
    except Exception:
        pass
    return False


def open_wechat():
    """
    打开/激活微信：优先点击任务栏中的微信图标；
    若未找到（微信未运行），则尝试启动微信 exe 或 wechat: 协议，再尝试点击任务栏。
    """
    import time
    if _click_wechat_taskbar_icon():
        return True
    # 未在任务栏找到，先启动微信
    exe = find_wechat_exe()
    if exe:
        try:
            subprocess.Popen([exe], shell=False)
        except Exception:
            pass
    else:
        try:
            os.startfile("wechat:")
        except Exception:
            pass
    time.sleep(2.0)
    return _click_wechat_taskbar_icon()


def show_wechat_send_prompt(message, wechat_opened):
    """弹出提示：若未登录请先登录，找到「AI奴隶主」并发送；内容已复制到剪贴板。"""
    from PyQt5.QtWidgets import QApplication, QMessageBox
    app = QApplication.instance() or QApplication(sys.argv)
    body = (
        "请找到名字为「AI奴隶主」的群聊/联系人，将比较结果发送过去。\n\n"
        "发送内容已复制到剪贴板，可在微信中直接粘贴（Ctrl+V）后发送。\n\n"
        "若当前未登录微信，请先登录后再发送。"
    )
    title = "发送 Cursor 用量汇报"
    if wechat_opened:
        QMessageBox.information(None, title, body)
    else:
        QMessageBox.warning(None, title, "未能自动打开微信，请手动打开微信。\n\n" + body)


def wechat_send_via_automation(full_message, contact_name="AI奴隶主"):
    """使用 pyautogui + pyperclip 在微信 PC 中打开指定联系人并发送消息。"""
    try:
        import pyautogui
        import time
    except ImportError:
        return False
    if not _clipboard_set_pyperclip(full_message):
        return False
    if not open_wechat():
        return False
    time.sleep(2.5)
    saved_clip = _clipboard_get_pyperclip()
    _clipboard_set_pyperclip(contact_name)
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "f")
    time.sleep(0.6)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.3)
    pyautogui.press("enter")
    time.sleep(0.8)
    _clipboard_set_pyperclip(full_message)
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.2)
    pyautogui.press("enter")
    if saved_clip != full_message:
        _clipboard_set_pyperclip(saved_clip)
    return True


def send_wechat_by_left_panel(contact_name="AI奴隶主", message="这是一条电脑自动发送的测试"):
    """
    微信发送流程（按坐标区域随机点击）：
    1. 打开微信
    2. 在搜索框 [2]-[4] 范围内随机点击 → 粘贴 contact_name → Enter
    3. 在输入框 [5]-[8] 范围内随机点击 → 粘贴 message
    4. 在发送键 [10]-[11] 范围内随机点击
    """
    try:
        import pyautogui
        import time
    except ImportError:
        return False

    if not open_wechat():
        return False
    time.sleep(1.5)

    saved_clip = _clipboard_get_pyperclip()

    # 1) 搜索框：在 [2]-[4] 范围内随机点击，粘贴「AI奴隶主」，Enter
    x_min, x_max, y_min, y_max = WECHAT_SEARCH_BOX_RANGE
    px, py = _random_point_in_range(x_min, x_max, y_min, y_max)
    pyautogui.moveTo(px, py, duration=0.2)
    pyautogui.click(px, py)
    time.sleep(0.25)
    _clipboard_set_pyperclip(contact_name)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1.0)
    pyautogui.press("enter")
    time.sleep(0.7)

    # 2) 输入框：在 [5]-[8] 范围内随机点击，粘贴发送内容
    x_min, x_max, y_min, y_max = WECHAT_INPUT_BOX_RANGE
    px, py = _random_point_in_range(x_min, x_max, y_min, y_max)
    pyautogui.moveTo(px, py, duration=0.2)
    pyautogui.click(px, py)
    time.sleep(0.2)
    _clipboard_set_pyperclip(message)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.15)

    # 3) 发送键：在 [10]-[11] 范围内随机点击
    x_min, x_max, y_min, y_max = WECHAT_SEND_BTN_RANGE
    px, py = _random_point_in_range(x_min, x_max, y_min, y_max)
    pyautogui.moveTo(px, py, duration=0.15)
    pyautogui.click(px, py)

    if saved_clip != message and saved_clip != contact_name:
        _clipboard_set_pyperclip(saved_clip)
    return True


def send_result_to_wechat(full_message, contact_name="AI奴隶主", use_automation=True):
    """打开微信，找到 contact_name 并发送 full_message；可选自动操作或仅复制+弹窗。"""
    set_clipboard(full_message)
    wechat_ok = open_wechat()
    if wechat_ok and use_automation and wechat_send_via_automation(full_message, contact_name):
        return
    show_wechat_send_prompt(full_message, wechat_ok)
