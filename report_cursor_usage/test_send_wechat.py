# -*- coding: utf-8 -*-
"""测试发送微信：打开微信，搜索 AI奴隶主，在聊天框/输入框/发送键区域随机点击并发送一条消息。"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from report_cursor_usage.wechat import send_wechat_by_left_panel

if __name__ == "__main__":
    ok = send_wechat_by_left_panel(
        contact_name="AI奴隶主",
        message="这是一条电脑自动发送的测试",
    )
    print("send_wechat_by_left_panel 返回:", ok)
