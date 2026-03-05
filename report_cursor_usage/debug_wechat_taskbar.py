# -*- coding: utf-8 -*-
"""调试：点击任务栏微信图标，逐步打印执行过程。"""
import os
import sys

def main():
    print("=== 调试：打开任务栏微信图标 ===\n")
    print("1. 平台:", sys.platform)
    if sys.platform != "win32":
        print("   仅支持 Windows，退出.")
        return

    print("2. 检查 pywinauto ...")
    try:
        from pywinauto import Application
        print("   已导入 pywinauto")
    except ImportError as e:
        print("   失败:", e)
        print("   建议: pip install --upgrade pywin32 pywinauto")
        _try_fallback()
        return

    print("3. 连接 explorer.exe (UIA) ...")
    try:
        app = Application(backend="uia").connect(path="explorer.exe")
        taskbar = app.window(class_name="Shell_TrayWnd")
        print("   任务栏窗口:", taskbar.window_text())
    except Exception as e:
        print("   失败:", e)
        return

    print("4. 按标题查找按钮 (微信 / Weixin / WeChat) ...")
    for name in ("微信", "Weixin", "WeChat", "WeChat.exe"):
        try:
            btn = taskbar.child_window(title=name, control_type="Button")
            if btn.exists(timeout=0):
                print("   找到: title=%r" % name)
                rect = btn.rectangle()
                print("   矩形: left=%s top=%s right=%s bottom=%s" % (rect.left, rect.top, rect.right, rect.bottom))
                cx = (rect.left + rect.right) // 2
                cy = (rect.top + rect.bottom) // 2
                print("   中心: (%s, %s)" % (cx, cy))
                print("5. 使用 pyautogui 移动并点击 ...")
                import pyautogui
                pyautogui.moveTo(cx, cy, duration=0.2)
                pyautogui.click(cx, cy)
                print("   已点击，结束.")
                return
        except Exception as e:
            print("   title=%r: %s" % (name, e))

    print("4b. 遍历任务栏所有 Button，按文本匹配 ...")
    try:
        for i, desc in enumerate(taskbar.descendants(control_type="Button")):
            try:
                t = ""
                if hasattr(desc, "window_text"):
                    w = desc.window_text
                    t = (w() if callable(w) else (w or "")) or ""
                if not t and getattr(desc, "element_info", None):
                    t = getattr(desc.element_info, "name", "") or ""
                if t and ("微信" in t or "WeChat" in t or "Weixin" in t):
                    print("   找到第 %d 个按钮: %r" % (i, t[:50]))
                    rect = desc.rectangle()
                    print("   矩形: left=%s top=%s right=%s bottom=%s" % (rect.left, rect.top, rect.right, rect.bottom))
                    cx = (rect.left + rect.right) // 2
                    cy = (rect.top + rect.bottom) // 2
                    print("5. 使用 pyautogui 移动并点击 ...")
                    import pyautogui
                    pyautogui.moveTo(cx, cy, duration=0.2)
                    pyautogui.click(cx, cy)
                    print("   已点击，结束.")
                    return
            except Exception as e:
                if i < 5:
                    print("   按钮 %d 异常: %s" % (i, e))
    except Exception as e:
        print("   遍历失败:", e)

    print("6. 未找到微信按钮，尝试图像匹配 ...")
    try:
        import pyautogui
        _dir = os.path.dirname(os.path.abspath(__file__))
        _icon = os.path.join(_dir, "wechat_taskbar_icon.png")
        print("   图标路径:", _icon, " 存在:", os.path.isfile(_icon))
        if os.path.isfile(_icon):
            screen_w, screen_h = pyautogui.size()
            region = (0, max(0, screen_h - 80), screen_w, 80)
            try:
                loc = pyautogui.locateOnScreen(_icon, region=region, confidence=0.8)
            except TypeError:
                loc = pyautogui.locateOnScreen(_icon, region=region)
            if loc:
                print("   找到图标位置:", loc)
                cx = loc.left + loc.width // 2
                cy = loc.top + loc.height // 2
                pyautogui.moveTo(cx, cy, duration=0.2)
                pyautogui.click(cx, cy)
                print("   已点击，结束.")
                return
            else:
                print("   未在任务栏区域匹配到图标.")
        else:
            print("   未放置 wechat_taskbar_icon.png，跳过图像匹配.")
    except Exception as e:
        print("   图像匹配失败:", e)

    print("\n=== 结果: 未能点击微信图标 ===")


def _try_fallback():
    """pywinauto 不可用时：尝试图像匹配 + wechat: 协议。"""
    print("\n--- 备用方案 ---")
    try:
        import pyautogui
    except ImportError:
        print("未安装 pyautogui，跳过图像匹配.")
        _start_wechat_protocol()
        return
    _dir = os.path.dirname(os.path.abspath(__file__))
    _icon = os.path.join(_dir, "wechat_taskbar_icon.png")
    if os.path.isfile(_icon):
        print("图像匹配: 在任务栏区域查找图标 ...")
        screen_w, screen_h = pyautogui.size()
        region = (0, max(0, screen_h - 80), screen_w, 80)
        try:
            loc = pyautogui.locateOnScreen(_icon, region=region, confidence=0.8)
        except TypeError:
            loc = pyautogui.locateOnScreen(_icon, region=region)
        if loc:
            cx = loc.left + loc.width // 2
            cy = loc.top + loc.height // 2
            pyautogui.moveTo(cx, cy, duration=0.2)
            pyautogui.click(cx, cy)
            print("已通过图像匹配点击，结束.")
            return
    print("未找到 wechat_taskbar_icon.png，无法用图像匹配.")
    _start_wechat_protocol()


def _start_wechat_protocol():
    try:
        os.startfile("wechat:")
        print("已调用 wechat: 协议启动微信，请查看是否弹出微信。")
    except Exception as e:
        print("wechat: 协议失败:", e)


if __name__ == "__main__":
    main()
