"""Merge the CI scan outputs into one machine-readable security-report.json.

Inputs (produced by the workflow, all optional):
  reports/bandit-report.json      bandit -f json
  reports/pip-audit-report.json   pip-audit -f json
  reports/pytest-report.xml       pytest --junitxml
  reports/validation-report.json  shared/validate_works.py --json
Output:
  reports/security-report.json
"""
import json
import os
import pathlib
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

REPORTS = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "reports")


def read_json(name: str):
    path = REPORTS / name
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return None


def bandit_summary(data) -> dict:
    if not data:
        return {"available": False}
    results = data.get("results", [])
    metrics = data.get("metrics", {}) or {}
    totals = {}
    for key, value in metrics.items():
        if isinstance(value, dict):
            for sev, count in value.items():
                if sev in ("SEVERITY.HIGH", "SEVERITY.MEDIUM", "SEVERITY.LOW", "SEVERITY.UNDEFINED"):
                    totals[sev.split(".")[-1].lower()] = totals.get(sev.split(".")[-1].lower(), 0) + count
    return {
        "available": True,
        "findings": len(results),
        "by_severity": totals,
        "issues": [
            {
                "file": r.get("filename"),
                "line": r.get("line_number"),
                "test": r.get("test_id"),
                "severity": r.get("issue_severity"),
                "text": (r.get("issue_text") or "").strip(),
            }
            for r in results[:50]
        ],
    }


def pip_audit_summary(data) -> dict:
    if not data:
        return {"available": False}
    deps = data.get("dependencies", []) or []
    vulnerable = [d for d in deps if d.get("vulns")]
    return {
        "available": True,
        "packages_checked": len(deps),
        "vulnerable_packages": len(vulnerable),
        "vulnerabilities": [
            {"package": d.get("name"), "version": d.get("version"), "id": v.get("id")}
            for d in vulnerable
            for v in d.get("vulns", [])
        ],
    }


def pytest_summary() -> dict:
    path = REPORTS / "pytest-report.xml"
    if not path.exists():
        return {"available": False}
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return {"available": False}
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        return {"available": False}
    return {
        "available": True,
        "tests": int(suite.get("tests", 0)),
        "failures": int(suite.get("failures", 0)),
        "errors": int(suite.get("errors", 0)),
        "skipped": int(suite.get("skipped", 0)),
        "time_seconds": float(suite.get("time", 0) or 0),
    }


def main() -> int:
    bandit = bandit_summary(read_json("bandit-report.json"))
    pip = pip_audit_summary(read_json("pip-audit-report.json"))
    tests = pytest_summary()
    works = read_json("validation-report.json") or {"available": False}

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repository": os.getenv("GITHUB_REPOSITORY", "local"),
        "commit": os.getenv("GITHUB_SHA", "local"),
        "run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT", "1"),
        "summary": {
            "bandit_findings": bandit.get("findings", 0),
            "pip_audit_vulnerabilities": pip.get("vulnerable_packages", 0),
            "tests_passed": tests.get("tests", 0) - tests.get("failures", 0) - tests.get("errors", 0),
            "tests_failed": tests.get("failures", 0) + tests.get("errors", 0),
            "works_checks": works.get("total", 0),
            "works_failed": works.get("failed", 0),
        },
        "sast_bandit": bandit,
        "sca_pip_audit": pip,
        "tests_pytest": tests,
        "works_validation": works,
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / "security-report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    s = report["summary"]
    print(f"security-report.json written to {out}")
    print(f"  bandit findings        : {s['bandit_findings']}")
    print(f"  pip-audit vulnerabilities: {s['pip_audit_vulnerabilities']}")
    print(f"  tests                  : {s['tests_passed']} passed, {s['tests_failed']} failed")
    print(f"  work checks            : {s['works_checks']} total, {s['works_failed']} failed")

    ok = (
        s["bandit_findings"] == 0
        and s["pip_audit_vulnerabilities"] == 0
        and s["tests_failed"] == 0
        and s["works_failed"] == 0
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
