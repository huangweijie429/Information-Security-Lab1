# HDU Information Security Labs

Four lab works (10 points each) from the HDU IS manual, kept in one repository.

| # | Work | Directory | Status |
|---|------|-----------|--------|
| 1 | Secure REST API + CI/CD + real CVE analysis | [`work1-api`](work1-api/README.md), [`work1-cve`](work1-cve/README.md) | in progress |
| 2 | Web application security audit (DAST + STRIDE) | [`work2-audit`](work2-audit/README.md) | planned |
| 3 | Computer attacks: digraph analysis | [`work3-attack`](work3-attack/README.md) | planned |
| 4 | Password audit, data leaks, digital hygiene | [`work4-hygiene`](work4-hygiene/README.md) | planned |

## Repository layout

```
.
├── .github/workflows/ci.yml   # SAST (bandit) + SCA (pip-audit) + pytest for the API
├── work1-api/                 # FastAPI service, JWT auth, parameterized SQL, escaped output
├── work1-cve/                 # vulnerable environment, PoC, fix and regression proof
├── work2-audit/               # Juice Shop DAST report, DFD + STRIDE, ZAP export
├── work3-attack/              # attack report, S0/Si/Sk digraph, presentation
├── work4-hygiene/             # password manager audit, leak check, hygiene rules
└── shared/                    # report template, diagram generator, cover page
```

## Quick start (Work 1 API)

```bash
cd work1-api
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
# open http://127.0.0.1:8000/docs
```

Default demo account: `admin` / `Admin123!` (override with `ADMIN_PASSWORD`, `JWT_SECRET`).

## CI

Every push and pull request runs `.github/workflows/ci.yml`: bandit (SAST),
pip-audit (SCA), then the pytest suite (including XSS/SQLi regression tests).
