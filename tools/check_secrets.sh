#!/usr/bin/env bash
# Fails if anything that looks like a credential is staged/tracked. The repo is PUBLIC.
# Usage: bash tools/check_secrets.sh   (run before every commit/push)
cd "$(dirname "$0")/.."
pat='(AIza[0-9A-Za-z_-]{35}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,}|xox[baprs]-[A-Za-z0-9-]{10,}|EAA[A-Za-z0-9]{40,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|(api[_-]?key|secret|password|token)["'"'"' ]*[:=]["'"'"' ]*[A-Za-z0-9_\-]{12,})'
hits=$(git ls-files -co --exclude-standard | grep -vE '\.(mp4|jpg|png|wav|onnx|ttc|otf|bz2)$' | xargs -d '\n' grep -nIE "$pat" 2>/dev/null | grep -v 'tools/check_secrets.sh')
if [ -n "$hits" ]; then echo "POSSIBLE SECRETS — do not push:"; echo "$hits"; exit 1; fi
echo "no secrets found"
