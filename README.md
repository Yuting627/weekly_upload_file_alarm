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
