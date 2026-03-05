# -*- coding: utf-8 -*-
"""
Cursor 应用余额/用量汇报 — 入口脚本。
功能已拆到 report_cursor_usage 包内各模块，此处仅调用包入口。
运行方式任选其一：
  python report_cursor_usage.py [参数...]
  python -m report_cursor_usage [参数...]
"""
from report_cursor_usage.cli import main

if __name__ == "__main__":
    main()
