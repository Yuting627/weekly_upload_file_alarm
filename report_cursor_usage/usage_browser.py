# -*- coding: utf-8 -*-
"""使用 Playwright 打开 Cursor spending 页并解析用量。"""
import re
import os
import sys

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    from . import config
    from .usage_api import parse_percentages_from_text
except ImportError:
    _pkg_dir = os.path.dirname(os.path.abspath(__file__))
    if _pkg_dir not in sys.path:
        sys.path.insert(0, _pkg_dir)
    import config
    from usage_api import parse_percentages_from_text


def fetch_usage_from_browser(headless=False, timeout_ms=30000, cookie_string=None):
    """
    用 Playwright 打开 Cursor spending 页，取文本并解析用量。
    返回 {"auto": 0.xx, "API": 0.xx} 或 None（失败时）。
    """
    if not HAS_PLAYWRIGHT:
        print("未安装 playwright，请执行: pip install playwright && playwright install chromium")
        return None

    url = "https://cursor.com/cn/dashboard?tab=spending"
    xpath = "/html/body/main/div/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[2]/div/div/div/div[3]"

    with sync_playwright() as p:
        browser = None
        try:
            browser = p.chromium.launch(headless=headless)
        except Exception as e:
            err_text = str(e)
            if "Executable doesn't exist" in err_text or "doesn't exist at" in err_text:
                try:
                    browser = p.chromium.launch(headless=headless, channel="chrome")
                except Exception as e2:
                    print("未检测到 Playwright 的 Chromium，且无法使用本机 Chrome。请任选其一：")
                    print("  1) 安装 Playwright 浏览器: playwright install chromium")
                    print("  2) 确认本机已安装 Chrome 并位于默认路径")
                    print(f"  错误: {e2}")
                    return None
            else:
                print(f"启动浏览器失败: {e}")
                return None
        try:
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                locale="zh-CN",
            )
            raw = cookie_string if cookie_string is not None else config.get_cursor_cookies()
            if raw:
                cookie_list = config.parse_cookie_string(raw)
                if cookie_list:
                    context.add_cookies(cookie_list)
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_timeout(5000)

            try:
                locator = page.locator(f"xpath={xpath}")
                locator.wait_for(state="visible", timeout=timeout_ms)
                text = locator.inner_text()
            except Exception:
                text = None

            if not text or not re.search(r"\d+(?:\.\d+)?\s*%", text):
                text = page.evaluate("""
                    () => { return document.body.innerText; }
                """)

            result = parse_percentages_from_text(text) if text else None
            context.close()
            return result
        finally:
            browser.close()
