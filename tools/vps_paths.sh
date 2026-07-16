#!/bin/sh
# vps_paths.sh — VPS path class definitions
#
# Source this file from any VPS readiness tool to get parameterized paths.
# Paths are NOT live production paths — they define *classes* of paths that
# Buddy/Strong Codex will populate with exact values.
#
# Usage:
#   . "$(dirname "$0")/vps_paths.sh"

set -eu

# ---- Repository root (auto-discovered) ----
VPS_REPO_ROOT="${VPS_REPO_ROOT:-}"
if [ -z "$VPS_REPO_ROOT" ]; then
    VPS_REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE:-$0}")/.." && pwd 2>/dev/null || echo "/home/scraper/apps/ivy-control-vps")
fi

# ---- State directory (outside public checkout) ----
# Default: $HOME/.ivy-control-vps  (set by Buddy for each host)
# On Mac:  $HOME/.ivy-control-vps
# On VPS:  $HOME/.ivy-control-vps or /home/scraper/.ivy-control-vps
VPS_STATE_DIR="${VPS_STATE_DIR:-"$HOME/.ivy-control-vps"}"

# ---- Sub-directories under state ----
VPS_GENERATED_DIR="${VPS_GENERATED_DIR:-"$VPS_STATE_DIR/generated"}"
VPS_CONFIG_DIR="${VPS_CONFIG_DIR:-"$VPS_STATE_DIR/config"}"
VPS_DATA_DIR="${VPS_DATA_DIR:-"$VPS_STATE_DIR/data"}"
VPS_LOG_DIR="${VPS_LOG_DIR:-"$VPS_STATE_DIR/logs"}"
VPS_BACKUP_DIR="${VPS_BACKUP_DIR:-"$VPS_STATE_DIR/backups"}"

# ---- Deployment registry (approved SHAs) ----
VPS_SHA_REGISTRY="${VPS_SHA_REGISTRY:-"$VPS_STATE_DIR/sha-registry.json"}"

# ---- Sanity check functions ----
vps_check_paths() {
    local fail=0
    for d in "$VPS_GENERATED_DIR" "$VPS_CONFIG_DIR" "$VPS_DATA_DIR" "$VPS_LOG_DIR" "$VPS_BACKUP_DIR"; do
        if [ ! -d "$d" ]; then
            printf -- 'MISSING: %s\n' "$d" >&2
            fail=1
        fi
    done
    return $fail
}

vps_ensure_dirs() {
    mkdir -p "$VPS_GENERATED_DIR" "$VPS_CONFIG_DIR" "$VPS_DATA_DIR" "$VPS_LOG_DIR" "$VPS_BACKUP_DIR"
}

vps_print_paths() {
    cat <<PATHS
VPS_REPO_ROOT=$VPS_REPO_ROOT
VPS_STATE_DIR=$VPS_STATE_DIR
VPS_GENERATED_DIR=$VPS_GENERATED_DIR
VPS_CONFIG_DIR=$VPS_CONFIG_DIR
VPS_DATA_DIR=$VPS_DATA_DIR
VPS_LOG_DIR=$VPS_LOG_DIR
VPS_BACKUP_DIR=$VPS_BACKUP_DIR
VPS_SHA_REGISTRY=$VPS_SHA_REGISTRY
PATHS
}
