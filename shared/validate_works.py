"""Validate that all four lab works are present and complete in the repository.

Runs inside CI (and locally): prints a table and exits non-zero if anything is missing.
No network access is needed.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
results: list[tuple[str, str, bool, str]] = []


def check(work: str, name: str, ok: bool, detail: str = "") -> None:
    results.append((work, name, bool(ok), detail))


def exists(rel: str) -> bool:
    return (ROOT / rel).is_file()


def read(rel: str) -> str:
    try:
        return (ROOT / rel).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


# ---------------------------------------------------------------- Work 1
check("Work 1", "API module", exists("work1-api/app/main.py"))
check("Work 1", "security module", exists("work1-api/app/security.py"))
check("Work 1", "database layer", exists("work1-api/app/db.py"))
check("Work 1", "test suite", exists("work1-api/tests/test_api.py"))
check("Work 1", "CI workflow", exists(".github/workflows/ci.yml"))
check("Work 1", "CVE environment", exists("work1-cve/docker-compose.yml"))
check("Work 1", "CVE PoC script", exists("work1-cve/poc.sh"))
cve_doc = read("work1-cve/README.md")
check("Work 1", "CVE-2018-12613 documented", "CVE-2018-12613" in cve_doc)
check("Work 1", "evidence files", len(list(ROOT.glob("work1-cve/evidence/*.txt"))) >= 4,
      f"{len(list(ROOT.glob('work1-cve/evidence/*.txt')))} files")

# ---------------------------------------------------------------- Work 2
check("Work 2", "DFD image", exists("work2-audit/dfd-en.png"))
check("Work 2", "audit report", exists("work2-audit/report-en.html"))
report2 = read("work2-audit/report-en.html")
check("Work 2", "STRIDE section", "STRIDE" in report2)
check("Work 2", "XSS evidence screenshot", exists("work2-audit/screenshots/02-xss-dom.png"))
try:
    zap = json.loads(read("work2-audit/zap-report.json") or "{}")
    alerts = sum(len(s.get("alerts", [])) for s in zap.get("site", []))
    check("Work 2", "ZAP export parses", alerts > 0, f"{alerts} alerts")
except json.JSONDecodeError:
    check("Work 2", "ZAP export parses", False, "invalid JSON")

# ---------------------------------------------------------------- Work 3
check("Work 3", "attack digraph", exists("work3-attack/digraph-en.png"))
check("Work 3", "attack report", exists("work3-attack/report-en.html"))
report3 = read("work3-attack/report-en.html")
check("Work 3", "states S0/Si/Sk described", "S<sub>0</sub>" in report3 and "S<sub>k</sub>" in report3)
check("Work 3", "presentation", exists("work3-attack/Work3-Presentation-EN.pptx"))

# ---------------------------------------------------------------- Work 4
check("Work 4", "hygiene report", exists("work4-hygiene/report-en.html"))
shots = list(ROOT.glob("work4-hygiene/screenshots-en/*.png"))
check("Work 4", "screenshots", len(shots) >= 4, f"{len(shots)} images")
check("Work 4", "TOTP generator page", exists("work4-hygiene/totp-en.html"))
report4 = read("work4-hygiene/report-en.html")
check("Work 4", "breach result documented", "Giant Tiger" in report4)

# ---------------------------------------------------------------- output
width = max(len(r[1]) for r in results) + 2
current = None
print(f"{'WORK':8} {'CHECK':<{width}} RESULT")
print("-" * (8 + width + 10))
for work, name, ok, detail in results:
    if work != current:
        print()
        current = work
    mark = "PASS" if ok else "FAIL"
    print(f"{work:8} {name:<{width}} {mark}  {detail}")

failed = [r for r in results if not r[2]]
print()
print(f"TOTAL {len(results)} checks, {len(results) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
