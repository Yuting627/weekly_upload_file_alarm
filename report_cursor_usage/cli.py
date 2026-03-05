# -*- coding: utf-8 -*-
"""CLI 入口：参数解析与主流程。"""
import json
import os
from datetime import date
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from . import config
from . import progress
from . import usage_api
from . import usage_browser
from . import wechat
from . import windows_utils


def _run_test_api():
    """仅测试 API：请求 get-current-period-usage，打印原始 JSON 与解析结果。"""
    raw = config.get_cursor_cookies()
    if not raw:
        print("未配置 Cookie（请创建 cursor_cookies.txt 或设置环境变量 CURSOR_COOKIES），无法请求 API。")
        return
    headers = {**usage_api.USAGE_API_HEADERS, "Cookie": raw.strip()}
    req = Request(usage_api.USAGE_API_URL, data=b"{}", headers=headers, method="POST")
    print("请求:", usage_api.USAGE_API_URL)
    print("Cookie 长度:", len(raw), "字符")
    try:
        with urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
        print("\n原始响应 JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        usage = usage_api.parse_usage_api_response(data)
        print("\n解析结果 (用于脚本):", usage)
        if usage:
            a, b = usage["auto"] * 100, usage["API"] * 100
            t = usage.get("totalPercentUsed", (usage["auto"] + usage["API"]) / 2) * 100
            print("百分比: autoPercentUsed={:.2f}%  apiPercentUsed={:.2f}%  totalPercentUsed={:.2f}%".format(a, b, t))
        else:
            print("解析失败，未得到 autoPercentUsed / apiPercentUsed / totalPercentUsed。")
    except HTTPError as e:
        print("HTTP 错误:", e.code, e.reason)
        if e.fp:
            try:
                print(e.fp.read().decode("utf-8")[:500])
            except Exception:
                pass
    except URLError as e:
        print("请求失败 (URLError):", e.reason)
    except (json.JSONDecodeError, OSError) as e:
        print("错误:", e)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cursor 用量汇报：获取 spending 并与目标进度比较")
    parser.add_argument("--no-browser", action="store_true", help="不打开浏览器，仅计算并输出目标进度")
    parser.add_argument("--headless", action="store_true", help="无头模式打开浏览器")
    parser.add_argument("--mock", type=str, metavar="JSON_OR_FILE", help='模拟数据：JSON 或文件路径')
    parser.add_argument("--mock-file", type=str, metavar="PATH", help="从文件读取模拟 JSON")
    parser.add_argument("--no-wechat", action="store_true", help="不打开微信、不弹窗")
    parser.add_argument("--no-wechat-auto", action="store_true", help="不自动操作微信，仅复制+弹窗")
    parser.add_argument("--test-api", action="store_true", help="仅测试 fetch_usage_from_api")
    parser.add_argument("--show-processes", action="store_true", help="仅显示当前运行的程序名称")
    parser.add_argument("--open-crashpad-handler", action="store_true", help="查找并打开 crashpad_handler.exe")
    parser.add_argument("--open-hidden-icons", action="store_true", help="打开 Windows 隐藏图标面板")
    args = parser.parse_args()

    if args.open_crashpad_handler:
        windows_utils.open_crashpad_handler()
        return
    if args.open_hidden_icons:
        windows_utils.open_windows_hidden_icons()
        return
    if args.show_processes:
        names = windows_utils.get_running_process_names()
        print("当前系统正在运行的程序名称（共 {} 个）:\n".format(len(names)))
        for i, name in enumerate(names, 1):
            print("  {:4d}. {}".format(i, name))
        return
    if args.test_api:
        _run_test_api()
        return

    today = date.today()
    target = progress.get_target_progress(today)
    target_pct = target * 100.0
    print(f"目标进度（每月2号起算）: {target_pct:.2f}%")

    if args.mock or args.mock_file:
        try:
            raw = None
            if args.mock_file:
                path = os.path.abspath(args.mock_file)
                if os.path.isfile(path):
                    with open(path, "r", encoding="utf-8") as f:
                        raw = f.read()
            if raw is None and args.mock:
                raw = args.mock
                if raw and (os.path.sep in raw or "/" in raw or raw.strip().endswith(".json")):
                    path = os.path.abspath(raw.strip().strip('"').strip("'"))
                    if os.path.isfile(path):
                        with open(path, "r", encoding="utf-8") as f:
                            raw = f.read()
            if not raw or not raw.strip():
                print("未提供有效 --mock 内容或 --mock-file 文件。")
                return
            data = json.loads(raw)

            def _n(v):
                return float(v) / 100.0 if float(v) > 1 else float(v)

            usage = {}
            if "autoPercentUsed" in data:
                usage["auto"] = _n(data["autoPercentUsed"])
            elif "auto" in data:
                usage["auto"] = _n(data["auto"])
            else:
                usage["auto"] = 0
            if "apiPercentUsed" in data:
                usage["API"] = _n(data["apiPercentUsed"])
            elif "API" in data or "api" in data:
                usage["API"] = _n(data.get("API") or data.get("api"))
            else:
                usage["API"] = 0
            if "totalPercentUsed" in data:
                usage["totalPercentUsed"] = _n(data["totalPercentUsed"])
            else:
                usage["totalPercentUsed"] = (usage["auto"] + usage["API"]) / 2
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"无效 --mock/--mock-file: {e}")
            print('提示: 建议用 --mock-file mock_usage.json')
            return
    elif args.no_browser:
        print("未获取网页数据（--no-browser）。使用 --mock 可传入模拟百分比。")
        return
    else:
        usage = usage_api.fetch_usage_from_api()
        if usage is None:
            usage = usage_browser.fetch_usage_from_browser(headless=args.headless)
        if usage is None:
            print("未能获取 auto/API 百分比（API 与页面抓取均失败），请检查 Cookie 或登录。")
            return

    auto_pct = round(usage["auto"] * 100, 2)
    api_pct = round(usage["API"] * 100, 2)
    total_pct = round(usage.get("totalPercentUsed", (usage["auto"] + usage["API"]) / 2) * 100, 2)
    print(f"目标进度: {target_pct:.2f}%")
    print(f"当前进度  auto: {auto_pct:.2f}%  |  api: {api_pct:.2f}%  |  total: {total_pct:.2f}%")

    out = {"autoPercentUsed": auto_pct, "apiPercentUsed": api_pct, "totalPercentUsed": total_pct}
    print(json.dumps(out, ensure_ascii=False))

    auto_conclusion, api_conclusion, total_conclusion = progress.compare_all_three(
        auto_pct, api_pct, total_pct, target_pct
    )
    print(f"进度结论  auto: {auto_conclusion}  |  api: {api_conclusion}  |  total: {total_conclusion}")

    if not args.no_wechat:
        conclusions = (auto_conclusion, api_conclusion, total_conclusion)
        full_message = progress.build_comparison_message(usage, target_pct, conclusions)
        wechat.send_result_to_wechat(full_message, use_automation=not args.no_wechat_auto)

    return {
        "autoPercentUsed": auto_pct,
        "apiPercentUsed": api_pct,
        "totalPercentUsed": total_pct,
        "targetProgress": target_pct,
        "autoConclusion": auto_conclusion,
        "apiConclusion": api_conclusion,
        "totalConclusion": total_conclusion,
    }


if __name__ == "__main__":
    main()
