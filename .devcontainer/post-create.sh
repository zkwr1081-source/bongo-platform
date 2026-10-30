#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install -r requirements.txt pytest

echo
echo "BONGO Codespace is ready."
echo "Run: bash scripts/dev-check.sh"
echo "No deployment or production service was started."
