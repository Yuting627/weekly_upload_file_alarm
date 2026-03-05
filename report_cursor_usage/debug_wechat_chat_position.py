# -*- coding: utf-8 -*-
"""
获取「聊天窗口」位置坐标的交互式工具。

用法：
  1. 运行: python report_cursor_usage/debug_wechat_chat_position.py
  2. 在任意位置点击鼠标，每点一下立即打印该点的屏幕坐标（及相对微信窗口的比例）。
  3. 点击次数不限；按 Ctrl+C 退出。
"""
import sys
import time


def main():
    if sys.platform != "win32":
        print("仅支持 Windows。")
        return

    try:
        from pynput.mouse import Listener
    except ImportError:
        print("请先安装: pip install pynput")
        return

    # 微信主窗口（用于计算相对比例，可选）
    rect = None
    try:
        from report_cursor_usage.windows_utils import get_window_rect
        rect = get_window_rect(title_substring="微信")
    except Exception:
        try:
            from .windows_utils import get_window_rect
            rect = get_window_rect(title_substring="微信")
        except Exception:
            pass

    if rect:
        print("【微信主窗口】 left=%s top=%s width=%s height=%s" % (rect["left"], rect["top"], rect["width"], rect["height"]))
    print("每点击一下返回一个坐标，按 Ctrl+C 退出。\n")

    count = [0]

    def on_click(x, y, button, pressed):
        if not pressed:
            return
        count[0] += 1
        line = "  [%d] x=%s, y=%s" % (count[0], x, y)
        if rect and rect.get("width") and rect.get("height"):
            rx = (x - rect["left"]) / rect["width"]
            ry = (y - rect["top"]) / rect["height"]
            line += "  | 相对窗口: width*%.3f, height*%.3f" % (rx, ry)
        print(line)

    with Listener(on_click=on_click) as listener:
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        try:
            listener.stop()
        except Exception:
            pass
    print("\n已退出。")


if __name__ == "__main__":
    main()
