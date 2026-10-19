# Work 1 — Secure REST API with CI/CD

FastAPI + SQLite service with JWT authentication, parameterized SQL and escaped output,
scanned by bandit (SAST) and pip-audit (SCA) on every push.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | no | liveness probe |
| POST | `/auth/login` | no | `{"username","password"}` → JWT |
| GET | `/api/data` | Bearer | posts list, optional `?q=` filter |
| GET | `/api/me` | Bearer | current user profile |

## Security measures

- **SQL injection** — every statement is parameterized (`?` placeholders); the login query
  and the `q` filter never concatenate user input. The username field is additionally
  allow-listed (`^[A-Za-z0-9_.-]+$`).
- **XSS** — all post fields are HTML-escaped with `html.escape()` before being returned;
  the regression test asserts `<b>` becomes `&lt;b&gt;`.
- **Authentication** — bcrypt (cost 12) password hashes, HS256 JWT with `exp`/`iss`,
  `HTTPBearer` dependency guarding every protected route.

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test

```bash
pip install -r requirements-dev.txt
pytest -q
```

## CI

`.github/workflows/ci.yml` runs on push and pull request: bandit → pip-audit → pytest.
