# -*- coding: utf-8 -*-
"""目标进度计算与用量比较结论。"""
from datetime import date
from calendar import monthrange

# 进度检查的差值阈值（%）：与目标进度之差在此范围内视为「刚刚好」
PROGRESS_DIFF_THRESHOLD = 0.5


def get_target_progress(today=None):
    """
    计算目标进度（按「每月2号」为起点的计费周期）。
    - 起始日期：当前月 2 号（若今天 < 2 号则用上月 2 号）
    - 总天数：起始日期所在月份的天数
    - 当月发生天数：今天 - 起始日期 + 1
    - 目标进度 = 发生天数 / 总天数（0~1，可转为百分比）
    """
    today = today or date.today()
    if today.day >= 2:
        start = date(today.year, today.month, 2)
    else:
        if today.month == 1:
            start = date(today.year - 1, 12, 2)
        else:
            start = date(today.year, today.month - 1, 2)
    year, month = start.year, start.month
    total_days = monthrange(year, month)[1]
    elapsed = (today - start).days + 1
    elapsed = max(0, min(elapsed, total_days))
    return elapsed / total_days if total_days else 0


def _compare_result(web_progress_pct, target_progress_pct):
    """返回比较结论字符串。差值阈值见 PROGRESS_DIFF_THRESHOLD（默认 0.5%）。"""
    diff = web_progress_pct - target_progress_pct
    if abs(diff) <= PROGRESS_DIFF_THRESHOLD:
        return "刚刚好，划算"
    elif diff > PROGRESS_DIFF_THRESHOLD:
        return "该省省啦"
    else:
        return "加油干啊"


def compare_and_print(web_progress_pct, target_progress_pct):
    """比较并打印单条结论。"""
    conclusion = _compare_result(web_progress_pct, target_progress_pct)
    print(conclusion)


def compare_all_three(auto_pct, api_pct, total_pct, target_pct):
    """对三个百分比分别与目标进度比较，返回 (auto结论, api结论, total结论)。"""
    return (
        _compare_result(auto_pct, target_pct),
        _compare_result(api_pct, target_pct),
        _compare_result(total_pct, target_pct),
    )


def build_comparison_message(usage, target_pct, conclusions):
    """
    拼成要发送的完整文案。
    conclusions: (auto结论, api结论, total结论) 或 单一结论字符串（兼容旧用法）。
    """
    auto_pct = round(usage["auto"] * 100, 2)
    api_pct = round(usage["API"] * 100, 2)
    total_pct = round(usage.get("totalPercentUsed", (usage["auto"] + usage["API"]) / 2) * 100, 2)
    if isinstance(conclusions, (list, tuple)) and len(conclusions) >= 3:
        auto_c, api_c, total_c = conclusions[0], conclusions[1], conclusions[2]
        lines = [
            "【Cursor 用量汇报】",
            f"目标进度（每月2号起）: {target_pct:.2f}%",
            f"autoPercentUsed: {auto_pct:.2f}% → {auto_c}",
            f"apiPercentUsed: {api_pct:.2f}% → {api_c}",
            f"totalPercentUsed: {total_pct:.2f}% → {total_c}",
        ]
    else:
        single = conclusions if isinstance(conclusions, str) else "—"
        lines = [
            "【Cursor 用量汇报】",
            f"目标进度（每月2号起）: {target_pct:.2f}%",
            f"autoPercentUsed: {auto_pct:.2f}%  apiPercentUsed: {api_pct:.2f}%  totalPercentUsed: {total_pct:.2f}%",
            f"结论: {single}",
        ]
    return "\n".join(lines)
