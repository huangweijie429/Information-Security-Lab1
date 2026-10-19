# 提交状态（STATUS）

最后更新：2026-10-19

| Work | 交付物 | 状态 | 位置 |
|---|---|---|---|
| 1 | FastAPI 应用 + 测试 + CI | ✅ CI 全绿（bandit / pip-audit / pytest） | `work1-api/`，Actions 运行记录见仓库 Actions 页 |
| 1 | CVE-2021-41773 复现与修复 | ✅ 漏洞版读到 `/etc/passwd`、RCE 得 `uid=1(daemon)`；修复版返回 400，回归通过 | `work1-cve/`，证据 `work1-cve/evidence/` |
| 2 | DAST + STRIDE 审计报告 | ✅ 6 页 PDF，12 条发现（3 条手工验证 + 9 条 ZAP） | `work2-audit/Work2-Audit-Report.pdf` |
| 2 | ZAP 导出 | ✅ HTML + JSON | `work2-audit/zap-report.*` |
| 2 | XSS 验证截图 | ✅ 真实执行证明（页面被注入脚本改写） | `work2-audit/screenshots/02-xss-dom.png` |
| 3 | 攻击分析报告 + 有向图 | ✅ 6 页 PDF + PNG + 8 页演示稿 | `work3-attack/` |
| 4 | 简报骨架 | 🟡 正文与规则已写，截图位待补 | `work4-hygiene/` |
| 4 | 截图（5 张） | ⛔ 需要本人账号 / 本机设置 | 见下 |

## Work 4 还差什么

| 截图 | 状态 | 说明 |
|---|---|---|
| `01-keepassxc-unlock.png` | ✅ 已生成 | KeePassXC 解锁界面（`--allow-screencapture` 绕过窗口捕获保护后截取） |
| `02-vault.png` | ✅ 已生成 | 密码库主界面，5 个账号条目 |
| `05-2fa.png` | ⛔ 待补 | 需要能开 TOTP 的真实账号（手机验证器） |
| `03-hibp.png` | ⛔ 待补 | 必须用本人邮箱查询，代查即伪造证据 |
| `06-social-audit.png` | ⛔ 待补 | 必须登录本人社交账号 |

补齐后把图片放进 `work4-hygiene/screenshots/`，重新生成 PDF：

```powershell
..\shared\build_pdf.ps1 -Html .\report.html -Pdf .\Work4-Hygiene-Report.pdf
```

## 环境说明（可复现）

- Docker 无法直装：Windows 组件存储损坏（DISM 14098），WSL2 功能无法启用；
  改用 **VirtualBox + boot2docker** 虚拟机 `hdu`（Docker 19.03）。
- 重启后需要恢复：`docker-machine start hdu`（`docker-machine.exe` 在 `D:\others\installers`），
  然后用封装脚本 `D:\others\bin\docker.ps1 <args>`。
- KeePassXC 为便携版：`D:\others\KeePassXC\KeePassXC-2.7.12-Win64\`。
