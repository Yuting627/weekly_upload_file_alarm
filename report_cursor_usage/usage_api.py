# -*- coding: utf-8 -*-
"""通过 Cursor API 获取当前周期用量。"""
import re
import json
import os
import sys
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

try:
    from . import config
except ImportError:
    _pkg_dir = os.path.dirname(os.path.abspath(__file__))
    if _pkg_dir not in sys.path:
        sys.path.insert(0, _pkg_dir)
    import config

USAGE_API_URL = "https://cursor.com/api/dashboard/get-current-period-usage"
USAGE_API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Origin": "https://cursor.com",
    "Referer": "https://cursor.com/cn/dashboard?tab=spending",
}


def parse_percentages_from_text(text):
    """
    从一段文字中解析前两个百分比，分别作为 auto 和 API。
    返回 {"auto": 0.xx, "API": 0.xx}，数值为 0~1；解析失败为 None。
    """
    if not text or not text.strip():
        return None
    pattern = re.compile(r"(\d+(?:\.\d+)?)\s*%")
    matches = pattern.findall(text)
    if len(matches) < 2:
        return None
    try:
        auto_pct = float(matches[0]) / 100.0
        api_pct = float(matches[1]) / 100.0
        return {"auto": auto_pct, "API": api_pct}
    except (ValueError, IndexError):
        return None


def _parse_usage_api_response(data):
    """从 API JSON 解析 autoPercentUsed, apiPercentUsed, totalPercentUsed。支持 usage / currentPeriodUsage / planUsage。"""
    if not data or not isinstance(data, dict):
        return None
    usage = (
        data.get("usage")
        or data.get("currentPeriodUsage")
        or data.get("planUsage")
        or data
    )
    if not isinstance(usage, dict):
        usage = data

    def _read_pct(obj, *keys):
        for k in keys:
            if k in obj and obj[k] is not None:
                v = obj[k]
                if isinstance(v, (int, float)):
                    return v / 100.0 if v > 1 else v
        return None

    auto_pct = _read_pct(usage, "autoPercentUsed", "auto", "autoUsage", "auto_percent")
    if auto_pct is None and "autoPercentUsed" in data:
        v = data["autoPercentUsed"]
        if isinstance(v, (int, float)):
            auto_pct = v / 100.0 if v > 1 else v
    api_pct = _read_pct(usage, "apiPercentUsed", "api", "apiUsage", "api_percent")
    if api_pct is None and "apiPercentUsed" in data:
        v = data["apiPercentUsed"]
        if isinstance(v, (int, float)):
            api_pct = v / 100.0 if v > 1 else v
    total_pct = _read_pct(usage, "totalPercentUsed", "total", "totalUsage")
    if total_pct is None and "totalPercentUsed" in data:
        v = data["totalPercentUsed"]
        if isinstance(v, (int, float)):
            total_pct = v / 100.0 if v > 1 else v

    if total_pct is None and (auto_pct is not None and api_pct is not None):
        total_pct = (auto_pct + api_pct) / 2.0
    if total_pct is None:
        return None
    if auto_pct is None:
        auto_pct = total_pct
    if api_pct is None:
        api_pct = total_pct

    return {"auto": auto_pct, "API": api_pct, "totalPercentUsed": total_pct}


def fetch_usage_from_api(cookie_string=None):
    """POST 请求 Cursor API 获取当前周期用量，返回 {"auto", "API", "totalPercentUsed"} 或 None。"""
    usage, _, _ = fetch_usage_from_api_with_error(cookie_string)
    return usage


def fetch_usage_from_api_with_error(cookie_string=None):
    """
    请求 API 获取用量；失败时返回 (None, 错误原因字符串, 原始响应)。
    返回 (usage_dict 或 None, error_message 或 None, api_response 或 None)。
    api_response 为接口返回的完整 JSON（dict），便于保存完整请求结果。
    """
    raw = cookie_string if cookie_string is not None else config.get_cursor_cookies()
    if not raw or not raw.strip():
        return None, "Cookie 为空，请配置 cursor_cookies.txt 或设置环境变量 CURSOR_COOKIES", None
    headers = {**USAGE_API_HEADERS, "Cookie": raw.strip()}
    req = Request(USAGE_API_URL, data=b"{}", headers=headers, method="POST")
    api_response = None
    try:
        with urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            api_response = data
    except HTTPError as e:
        err_msg = "HTTP {} {}".format(e.code, e.reason or "")
        try:
            raw_body = e.read().decode("utf-8")
            api_response = json.loads(raw_body)
        except Exception:
            pass
        return None, err_msg, api_response
    except URLError as e:
        return None, "请求失败: {}".format(getattr(e, "reason", str(e))), None
    except json.JSONDecodeError as e:
        return None, "响应非 JSON: {}".format(e), None
    except OSError as e:
        return None, "网络或超时: {}".format(e), None
    usage = _parse_usage_api_response(data)
    if usage is None:
        return None, "响应中未解析到 autoPercentUsed/apiPercentUsed/totalPercentUsed", api_response
    return usage, None, api_response


def parse_usage_api_response(data):
    """对外暴露：从 API 返回的 JSON 解析用量（供测试等使用）。"""
    return _parse_usage_api_response(data)


def fetch_and_save(cookie_string=None, out_dir=None):
    """
    请求 API 获取用量，打印结果，并保存到带时间戳的文件。
    保存内容包含汇总字段与完整 API 响应（apiResponse）。
    out_dir: 保存目录，默认项目根目录（包所在目录的上一级）。
    返回 (结果 dict 或 None, 保存路径或 None)。
    """
    usage, error_detail, api_response = fetch_usage_from_api_with_error(cookie_string)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if out_dir is None:
        out_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(out_dir, exist_ok=True)
    filename = "cursor_usage_{}.json".format(ts)
    filepath = os.path.join(out_dir, filename)

    if usage is None:
        result = {
            "timestamp": ts,
            "error": "未能获取用量",
            "detail": error_detail or "Cookie 无效或请求失败",
        }
        if api_response is not None:
            result["apiResponse"] = api_response
        print(json.dumps(result, ensure_ascii=False, indent=2))
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("已保存:", filepath)
        return None, filepath

    auto_pct = round(usage["auto"] * 100, 2)
    api_pct = round(usage["API"] * 100, 2)
    total_pct = round(usage.get("totalPercentUsed", (usage["auto"] + usage["API"]) / 2) * 100, 2)
    result = {
        "timestamp": ts,
        "autoPercentUsed": auto_pct,
        "apiPercentUsed": api_pct,
        "totalPercentUsed": total_pct,
    }
    if api_response is not None:
        result["apiResponse"] = api_response
    print(json.dumps(result, ensure_ascii=False, indent=2))
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("已保存:", filepath)
    return result, filepath


if __name__ == "__main__":
    fetch_and_save()
