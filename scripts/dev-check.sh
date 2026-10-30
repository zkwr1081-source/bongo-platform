#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== Python syntax check =="
python -m compileall -q bongo nexora tests

echo
echo "== Test suite =="
python -m pytest -q

echo
echo "Development checks completed."
