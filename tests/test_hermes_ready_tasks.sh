#!/usr/bin/env bash
# Tests for tools/hermes_ready_tasks.sh
set -eu

SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/tools/hermes_ready_tasks.sh"
PASS=0
FAIL=0

pass() { PASS=$((PASS+1)); }
fail() { FAIL=$((FAIL+1)); echo "FAIL: $1"; }

# Test table format
output=$("$SCRIPT" --format table 2>/dev/null) || true
if echo "$output" | grep -q "REPO"; then
    pass
else
    fail "table output missing header"
fi

# Test repo filter
output=$("$SCRIPT" --repo palworld-kb 2>/dev/null) || true
if echo "$output" | grep -q "palworld-kb"; then
    pass
else
    fail "repo filter missing palworld-kb"
fi

# Test json format
output=$("$SCRIPT" --format json 2>/dev/null) || true
if echo "$output" | grep -q '"tasks"'; then
    pass
else
    fail "json output missing tasks"
fi
if echo "$output" | grep -q '"lifecycle"'; then
    pass
else
    fail "json output missing lifecycle fields"
fi

# Test markdown format
output=$("$SCRIPT" --format markdown 2>/dev/null) || true
if echo "$output" | grep -q "| Repo"; then
    pass
else
    fail "markdown output missing header"
fi

# Test no-args defaults to table
output=$("$SCRIPT" 2>/dev/null) || true
if echo "$output" | grep -q "REPO"; then
    pass
else
    fail "default format not table"
fi

# Test no secrets in output
output=$("$SCRIPT" 2>/dev/null) || true
if echo "$output" | grep -q "/Users/"; then
    # Allow redacted form
    if echo "$output" | grep -q "<local-path>"; then
        pass
    else
        fail "raw local path in output"
    fi
else
    pass
fi

# Test exit code on success
if "$SCRIPT" > /dev/null 2>&1; then
    pass
else
    fail "non-zero exit on normal run"
fi

echo "---"
echo "Passed: $PASS"
echo "Failed: $FAIL"
[ "$FAIL" -eq 0 ] || exit 1
