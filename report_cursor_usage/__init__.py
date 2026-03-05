# -*- coding: utf-8 -*-
"""
Cursor 应用余额/用量汇报工具包。

各模块可独立使用：
- config: Cookie 配置与解析
- progress: 目标进度计算、用量比较结论、汇报文案
- usage_api: 通过 Cursor API 获取用量
- usage_browser: 通过 Playwright 打开 spending 页获取用量
- wechat: 打开微信、剪贴板、自动发送到指定联系人
- windows_utils: 进程列表、crashpad_handler、隐藏图标面板
- cli: 命令行入口 main()
"""
from .config import (
    COOKIES_FILE,
    get_cursor_cookies,
    load_cursor_cookies,
    parse_cookie_string,
)
from .progress import (
    PROGRESS_DIFF_THRESHOLD,
    build_comparison_message,
    compare_all_three,
    compare_and_print,
    get_target_progress,
)
from .usage_api import (
    USAGE_API_HEADERS,
    USAGE_API_URL,
    fetch_usage_from_api,
    parse_percentages_from_text,
    parse_usage_api_response,
)
from .usage_browser import fetch_usage_from_browser
from .wechat import (
    open_wechat,
    send_result_to_wechat,
    send_wechat_by_left_panel,
    set_clipboard,
    wechat_send_via_automation,
)
from .windows_utils import (
    get_running_process_names,
    get_window_rect,
    list_window_titles,
    find_crashpad_handler_exe,
    open_crashpad_handler,
    open_windows_hidden_icons,
)
from .cli import main

__all__ = [
    "main",
    "get_cursor_cookies",
    "load_cursor_cookies",
    "parse_cookie_string",
    "COOKIES_FILE",
    "get_target_progress",
    "PROGRESS_DIFF_THRESHOLD",
    "compare_and_print",
    "compare_all_three",
    "build_comparison_message",
    "fetch_usage_from_api",
    "parse_percentages_from_text",
    "parse_usage_api_response",
    "USAGE_API_URL",
    "USAGE_API_HEADERS",
    "fetch_usage_from_browser",
    "set_clipboard",
    "open_wechat",
    "send_result_to_wechat",
    "send_wechat_by_left_panel",
    "wechat_send_via_automation",
    "get_running_process_names",
    "get_window_rect",
    "list_window_titles",
    "find_crashpad_handler_exe",
    "open_crashpad_handler",
    "open_windows_hidden_icons",
]
