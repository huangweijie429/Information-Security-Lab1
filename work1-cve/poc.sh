#!/usr/bin/env bash
# Probe CVE-2018-12613 (phpMyAdmin 4.8.1 local file inclusion).
# Usage: ./poc.sh [base-url]   (default http://127.0.0.1:8080)
# Exit 0 when the payload is blocked, 1 when a file is disclosed.
# Only bash built-ins are used for parsing, so it also runs under Git Bash on Windows.
set -u
base="${1:-http://127.0.0.1:8080}"
fail=0

check () {
  local name="$1" path="$2" needle="$3" resp code body
  resp=$(curl --path-as-is -s -m 15 -w '\n%{http_code}' "$base/$path" 2>/dev/null)
  code="${resp##*$'\n'}"
  body="${resp%$'\n'*}"

  case "$body" in
    *"$needle"*)
      printf '[VULNERABLE] %-34s HTTP %s - file content disclosed\n' "$name" "$code"
      fail=1
      ;;
    *)
      printf '[blocked]    %-34s HTTP %s\n' "$name" "$code"
      ;;
  esac
}

echo "Target: $base"
check "target parameter traversal" "index.php?target=db_sql.php%253f/../../../../../../../../etc/passwd" "root:x:0:0"
check "hosts file traversal"       "index.php?target=db_sql.php%253f/../../../../../../../../etc/hosts" "localhost"

echo "----"
if [ "$fail" -eq 0 ]; then
  echo "RESULT: payloads blocked (fix verified)"
else
  echo "RESULT: at least one payload leaked a file (vulnerable)"
fi
exit "$fail"
