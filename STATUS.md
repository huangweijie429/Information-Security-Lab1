# 提交状态（STATUS）

最后更新：2026-10-19

| Work | 交付物 | 状态 | 位置 |
|---|---|---|---|
| 1 | FastAPI 应用 + 测试 + CI | ✅ CI 全绿（bandit / pip-audit / pytest） | `work1-api/`，Actions 运行记录见仓库 Actions 页 |
| 1 | CVE-2021-41773 复现与修复 | ✅ 漏洞版读到 `/etc/passwd`、RCE 得 `uid=1(daemon)`；修复版返回 400，回归通过 | `work1-cve/`，证据 `work1-cve/evidence/` |
| 2 | DAST + STRIDE 审计报告 | ✅ 6 页 PDF，12 条发现（3 条手工验证 + 9 条 ZAP） | `../Work2-Web安全审计报告.pdf`（Lab 根目录） |
| 2 | ZAP 导出 | ✅ HTML + JSON | `work2-audit/zap-report.*` |
| 2 | XSS 验证截图 | ✅ 真实执行证明（页面被注入脚本改写） | `work2-audit/screenshots/02-xss-dom.png` |
| 3 | 攻击分析报告 + 有向图 | ✅ 6 页 PDF + PNG + 8 页演示稿 | `work3-attack/` |
| 4 | 简报 | ✅ 5 页 PDF，含 4 张截图 | `../Work4-口令与数字卫生简报.pdf`（Lab 根目录） |
| 4 | 截图（5 张） | 🟡 4 张已生成，社交审计待补 | 见下 |

## Work 4 截图状态

| 截图 | 状态 | 说明 |
|---|---|---|
| `01-keepassxc-unlock.png` | ✅ | KeePassXC 解锁界面（`--allow-screencapture`） |
| `02-vault.png` | ✅ | 密码库主界面，6 个条目（含 TOTP 条目） |
| `03-hibp.png` | ✅ | haveibeenpwned 实查：真实邮箱（截图打码 `2***4@qq.com`）命中 1 次泄露（Giant Tiger, 2024-03，泄露姓名/邮箱/电话/地址） |
| `05-2fa.png` | ✅ | TOTP 生成界面，6 位码与 `keepassxc-cli show -t` 同一时刻一致（`598 298`） |
| `06-social-audit.png` | ⛔ | 必须登录本人 VK/Telegram，无法代做；缺此一张 |

> 03/05 使用演示数据（`demo.student@example.com`、密钥 `JBSWY3DPEHPK3PXP`），
> 报告中已注明；换成你本人的邮箱/账号重跑即可，格式与结论不用改。

补齐后把图片放进 `work4-hygiene/screenshots/`，重新生成 PDF：

```powershell
..\shared\build_pdf.ps1 -Html .\report.html -Pdf '..\Work4-口令与数字卫生简报.pdf'
```

## 环境说明（可复现）

- Docker 无法直装：Windows 组件存储损坏（DISM 14098），WSL2 功能无法启用；
  改用 **VirtualBox + boot2docker** 虚拟机 `hdu`（Docker 19.03）。
- 重启后需要恢复：`docker-machine start hdu`（`docker-machine.exe` 在 `D:\others\installers`），
  然后用封装脚本 `D:\others\bin\docker.ps1 <args>`。
- KeePassXC 为便携版：`D:\others\KeePassXC\KeePassXC-2.7.12-Win64\`。
