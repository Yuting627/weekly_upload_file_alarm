# 每周发布跟踪提醒 - 定时任务

每周一 **下午 3:00** 自动：
1. 弹出闹钟提醒对话框  
2. 打开文件夹 `E:\du\WR\weekly_new_release_track`  
3. 用 Chrome 打开 Box 链接：<https://app.box.com/folder/359316630190?tc=collab-folder-invite-treatment-b>

**GitHub：** [https://github.com/Yuting627/weekly_upload_file_alarm](https://github.com/Yuting627/weekly_upload_file_alarm)

```bash
git clone https://github.com/Yuting627/weekly_upload_file_alarm.git
```

### 更新到 GitHub（本地改完后推送）

在项目目录下执行：

```bash
git add .
git commit -m "简要说明本次修改"
git push
```

- 首次推送或未配置过时，可能需登录 GitHub（建议使用 [Personal Access Token](https://github.com/settings/tokens) 作为密码）。

---

## 使用步骤

### 1. 注册计划任务（只需做一次）

双击运行 **`register_weekly_task.bat`**。

- 若提示“创建任务失败”，请 **右键 → 以管理员身份运行** 再试。  
- 成功后可在 Windows **任务计划程序** 中看到任务名：`WeeklyReleaseTrackReminder`。

### 2. 测试（不等到周一）

双击 **`立即测试提醒.bat`**，会立刻执行一次：弹窗、打开文件夹、用 Chrome 打开链接，用于检查是否正常。

### 3. 删除计划任务

若不再需要定时提醒，双击 **`删除计划任务.bat`** 即可移除该任务。

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `run_weekly_reminder.ps1` | 主脚本：启动 Qt 弹窗，点击「打开」后执行打开文件夹与 Chrome |
| `reminder_dialog.py` | Qt 弹窗（PyQt5 + QSS），闹钟图标、Calibri 字体，可拖动 |
| `Alarm Clock.svg` | 闹钟图标 |
| `requirements.txt` | Python 依赖：PyQt5 |
| `register_weekly_task.bat` | 注册「每周一 15:00」的 Windows 计划任务 |
| `立即测试提醒.bat` | 立即执行一次提醒，用于测试 |
| `删除计划任务.bat` | 删除已注册的计划任务 |

---

## 注意事项

- 需安装 **Python 3** 和 **PyQt5**（`pip install -r requirements.txt`）。  
- 每周一 15:00 时电脑需处于开机状态且已登录，任务才会执行。  
- 若未安装 Chrome，脚本会用系统默认浏览器打开 Box 链接。  
- 文件夹 `E:\du\WR\weekly_new_release_track` 若不存在，仍会打开 Box 链接。


---

## 定时汇报 Cursor 应用余额

脚本 `report_cursor_usage.py` 用于汇报 Cursor Dashboard 的用量（auto/API 百分比），并与「每月 2 号起算」的目标进度比较。**功能已拆到 `report_cursor_usage/` 包内，各模块可独立使用。**

### 逻辑说明

1. **从网页获取用量**
   - 用 Playwright 打开：<https://cursor.com/cn/dashboard?tab=spending>
   - 需先登录 → 进入 Dashboard → Spending 标签
   - 从页面指定区域取文字，解析**第一个百分比**为 auto 用量、**第二个百分比**为 API 用量
   - 返回格式：`{"auto": 百分比, "API": 百分比}`（如 `{"auto": 15.2, "API": 8.1}`）

2. **目标进度**
   - 起始日期：当前月 2 号（若今天 < 2 号则为上月 2 号）
   - 总天数：起始日期所在月份的天数
   - 当月发生天数：今天 − 起始日期 + 1
   - 目标进度 = 当月发生天数 / 总天数

3. **比较与提示**
   - 用 (auto + API) / 2 作为「web 获取的进度」与目标进度比较
   - 差距在 **5% 以内**：输出「刚刚好，划算」
   - 比目标**大 0.5% 以上**：输出「该省省啦」
   - 比目标**小 0.5% 以上**：输出「加油干啊」

4. **打开微信并发送结果**（默认开启，可用 `--no-wechat` 关闭）
   - 自动尝试打开微信（按常见安装路径启动）。
   - 若未登录：弹窗提示「若当前未登录微信，请先登录后再发送」。
   - 提示用户找到名字为「**AI奴隶主**」的群聊/联系人。
   - 将比较结果（目标进度、auto/API 百分比、结论）复制到剪贴板，用户可在微信中粘贴（Ctrl+V）后发送。

### Cookie 配置（登录 Cursor 用）

用量获取（API 或页面抓取）需要 Cursor 登录态，通过 **Cookie** 提供，任选其一：

- **推荐：配置文件**  
  在脚本同目录下创建 `cursor_cookies.txt`，将浏览器里复制的整段 Cookie 粘贴进去（一行即可）。  
  可参考 `cursor_cookies.txt.example` 说明。**勿将 `cursor_cookies.txt` 提交到 Git**（已加入 .gitignore）。
- **环境变量**  
  设置环境变量 `CURSOR_COOKIES` 为 Cookie 字符串，可覆盖配置文件。

### 请求头说明（fetch_usage_from_api）

调用 `https://cursor.com/api/dashboard/get-current-period-usage` 时，建议使用以下 **Request Headers**：

| Header | 是否必需 | 说明 |
|--------|----------|------|
| **Cookie** | 必需 | 登录 Cursor 后的完整 Cookie，用于鉴权。 |
| **Content-Type** | 必需 | `application/json`（POST body 为 `{}`）。 |
| **User-Agent** | 建议 | 与浏览器一致，如 Chrome 145，避免被识别为脚本。 |
| **Accept** | 建议 | `application/json` 或 `*/*`。 |
| **Origin** | 建议 | `https://cursor.com`，与站同源。 |
| **Referer** | 建议 | `https://cursor.com/cn/dashboard?tab=spending`。 |

请求方法：**POST**，Body：`{}`。

### 依赖与安装

```bash
pip install -r requirements.txt
playwright install chromium
```

### 使用方式

```bash
# 打开浏览器并抓取 spending 页，输出 JSON 与提示
python report_cursor_usage.py

# 无头模式（不显示浏览器窗口）
python report_cursor_usage.py --headless

# 不打开微信、不弹窗提示发送（仅控制台输出）
python report_cursor_usage.py --no-wechat

# 仅计算目标进度，不访问网页
python report_cursor_usage.py --no-browser

# 用本地数据模拟（用于测试比较逻辑）
python report_cursor_usage.py --mock-file mock_usage.json
# 或传入 JSON 字符串（PowerShell 下引号需转义，建议用 --mock-file）
python report_cursor_usage.py --mock "{\"autoPercentUsed\":15,\"apiPercentUsed\":8,\"totalPercentUsed\":12}"
```
（Windows 下若 `--mock` 报「Expecting property name enclosed in double quotes」等错误，请改用 `--mock-file mock_usage.json` 或按上例转义双引号。）

**其他参数（Windows）：**
- `--open-hidden-icons`：打开任务栏「隐藏图标」面板（模拟 Win+B、Enter），打开后可用方向键选择图标，Enter 启动对应程序。
- `--show-processes`：仅列出当前正在运行的程序名称。
- `--open-crashpad-handler`：查找并启动 Chrome 的 crashpad_handler.exe。

首次运行会打开 Cursor 页面，需手动登录；后续可使用同一环境保留登录态（若需持久化可改用 Playwright 的 `storage_state`）。

微信步骤会尝试启动本机微信；若微信未安装或路径不同，会提示「请手动打开微信」，内容仍会复制到剪贴板便于粘贴发送。

### 包结构（report_cursor_usage/）

| 模块 | 说明 | 独立使用示例 |
|------|------|--------------|
| `config` | Cookie 配置与解析 | `from report_cursor_usage import get_cursor_cookies` |
| `progress` | 目标进度、比较结论、汇报文案 | `from report_cursor_usage import get_target_progress, compare_all_three` |
| `usage_api` | 通过 API 获取用量 | `from report_cursor_usage import fetch_usage_from_api` |
| `usage_browser` | 通过 Playwright 抓取 spending 页 | `from report_cursor_usage import fetch_usage_from_browser` |
| `wechat` | 打开微信、剪贴板、自动发送 | `from report_cursor_usage import send_result_to_wechat` |
| `windows_utils` | 进程列表、crashpad、隐藏图标 | `from report_cursor_usage import get_running_process_names` |
| `cli` | 命令行入口 | `from report_cursor_usage import main; main()` |

运行方式任选其一：`python report_cursor_usage.py [参数...]` 或 `python -m report_cursor_usage [参数...]`。


## 操作微信

- 使用 **pyautogui** 模拟键盘操作、**pyperclip** 处理剪贴板，避免中文与特殊字符出错。
- 流程：先打开微信 PC 客户端 → **Ctrl+F** 打开搜索 → 用剪贴板粘贴联系人名「AI奴隶主」→ **Enter** 打开该聊天 → 粘贴汇报内容 → **Enter** 发送。
- 依赖：`pip install pyautogui pyperclip`（已写入 `requirements.txt`）。若未安装或自动化失败，会退化为：复制内容到剪贴板并弹窗，提示用户手动在微信中找到「AI奴隶主」后粘贴发送。
- 若不想自动操作微信，仅要复制+提示，可加参数：`--no-wechat-auto`。

