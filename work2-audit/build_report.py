"""Build the Work 2 audit report from the ZAP JSON export + HTML template."""
import html
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
TEMPLATE = HERE / "report.template.html"
ZAP_JSON = HERE / "zap-report.json"
OUT = HERE / "report.html"

VERIFIED = {
    "SQL Injection": "SQLi 登录绕过已复现（返回 admin JWT）",
    "Cross Site Scripting (Reflected)": "搜索框 DOM XSS 已复现",
    "Cross Site Scripting (DOM Based)": "搜索框 DOM XSS 已复现",
    "Cross Site Scripting (Persistent)": "评论字段存储型 XSS 已复现",
}

RISK_CLASS = {"High": "#b3261e", "Medium": "#b5761f", "Low": "#4a6fb5", "Informational": "#5a5a5a"}


def load_alerts():
    if not ZAP_JSON.exists():
        return []
    data = json.loads(ZAP_JSON.read_text(encoding="utf-8", errors="ignore"))
    out = []
    for site in data.get("site", []):
        out.extend(site.get("alerts", []))
    return out


def row(a):
    name = a.get("alert", "")
    risk = (a.get("riskdesc", "").split(" (")[0] or "Informational").strip()
    conf = re.search(r"\((.*?)\)", a.get("riskdesc", ""))
    instances = a.get("instances", [])
    uri = instances[0].get("uri", "") if instances else ""
    param = instances[0].get("param", "") if instances else ""
    evidence = instances[0].get("evidence", "") if instances else ""
    cwe = a.get("cweid", "")
    verified = VERIFIED.get(name, "")
    colour = RISK_CLASS.get(risk, "#5a5a5a")
    return (
        "<tr>"
        f'<td><span style="color:{colour};font-weight:700">{html.escape(risk)}</span><br>'
        f'<span class="small">confidence: {html.escape(conf.group(1) if conf else "-")}</span></td>'
        f"<td><b>{html.escape(name)}</b><br><span class=\"small\">CWE-{html.escape(str(cwe))}</span></td>"
        f'<td><code>{html.escape(uri[:110])}</code><br><span class="small">param: {html.escape(param or "-")}</span></td>'
        f'<td class="small">{html.escape(evidence[:120] or "-")}</td>'
        f"<td>{'✔ ' + html.escape(verified) if verified else '—'}</td>"
        "</tr>"
    )


def main():
    alerts = load_alerts()
    order = {"High": 0, "Medium": 1, "Low": 2, "Informational": 3}
    alerts.sort(key=lambda a: order.get((a.get("riskdesc", "").split(" (")[0] or "").strip(), 9))

    shown = [a for a in alerts if (a.get("riskdesc", "").split(" (")[0] or "").strip() in ("High", "Medium")][:12]
    if len(shown) < 5:
        shown = alerts[:12]

    manual = [
        ("High", "SQL Injection（登录认证绕过）", "POST /rest/user/login", "\"email\":\"' OR 1=1--\" → 返回 admin JWT（784 B）", "✔ 已复现"),
        ("High", "DOM / Reflected XSS（搜索框）", "/#/search?q=", "查询串原样写入 DOM，<iframe src=javascript:alert(1)> 被执行", "✔ 已复现"),
        ("Medium", "目录浏览 / 敏感文件暴露", "/ftp", "ZAP 发现 /ftp 可直接访问并列出备份文件", "✔ 已确认"),
    ]

    manual_colour = {"High": "#b3261e", "Medium": "#b5761f"}
    manual_html = "\n".join(
        f'<tr><td><span style="color:{manual_colour.get(r, "#5a5a5a")};font-weight:700">{r}</span></td>'
        f"<td><b>{html.escape(n)}</b></td><td><code>{html.escape(loc)}</code></td>"
        f'<td class="small">{html.escape(ev)}</td><td>{html.escape(v)}</td></tr>'
        for r, n, loc, ev, v in manual
    )
    rows = manual_html + "\n" + "\n".join(row(a) for a in shown)
    table = (
        '<table class="data">\n'
        "<tr><th style=\"width:14%\">风险</th><th style=\"width:26%\">漏洞</th>"
        "<th style=\"width:28%\">位置</th><th>证据</th><th style=\"width:16%\">手工验证</th></tr>\n"
        f"{rows}\n</table>"
    )

    doc = TEMPLATE.read_text(encoding="utf-8")
    doc = doc.replace("<!--FINDINGS-->", table)
    doc = doc.replace("<!--ZAP_COUNT-->", str(len(alerts)))
    doc = doc.replace("<!--ZAP_HIGH-->", str(sum(1 for a in alerts if a.get("riskdesc", "").startswith("High"))))
    doc = doc.replace("<!--ZAP_MEDIUM-->", str(sum(1 for a in alerts if a.get("riskdesc", "").startswith("Medium"))))
    doc = doc.replace("<!--VERIFIED_COUNT-->", str(len(manual) + sum(1 for a in alerts if a.get("alert") in VERIFIED)))
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT} with {len(shown)} findings (of {len(alerts)} alerts)")


if __name__ == "__main__":
    main()
