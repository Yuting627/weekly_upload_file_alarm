# -*- coding: utf-8 -*-
"""Cursor 用量汇报相关配置：Cookie 等。"""
import os

# Cookie 配置文件：项目根目录下的 cursor_cookies.txt
_CONFIG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIES_FILE = os.path.join(_CONFIG_DIR, "cursor_cookies.txt")


def load_cursor_cookies():
    """从配置文件或环境变量读取 Cursor Cookie。优先：cursor_cookies.txt > 环境变量 CURSOR_COOKIES。"""
    if os.path.isfile(COOKIES_FILE):
        try:
            with open(COOKIES_FILE, "r", encoding="utf-8") as f:
                raw = f.read().strip()
            if raw:
                return raw
        except OSError:
            pass
    return os.environ.get("CURSOR_COOKIES", "").strip()


def get_cursor_cookies():
    """获取当前 Cursor Cookie（从配置文件或环境变量）。"""
    return load_cursor_cookies()


def parse_cookie_string(cookie_string, domain=".cursor.com", path="/"):
    """
    将 "name1=value1; name2=value2" 解析为 Playwright add_cookies 所需的列表。
    若 value 中含 '='，只按第一个 '=' 分割。
    """
    if not cookie_string or not cookie_string.strip():
        return []
    cookies = []
    for part in cookie_string.strip().split(";"):
        part = part.strip()
        if not part:
            continue
        eq = part.find("=")
        if eq <= 0:
            continue
        name, value = part[:eq].strip(), part[eq + 1 :].strip()
        if name:
            cookies.append({"name": name, "value": value, "domain": domain, "path": path})
    return cookies
