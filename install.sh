#!/bin/bash
# Turing Complete 한국어 패치 설치 스크립트 (Linux / macOS)
#
# 릴리즈 바이너리(patcher_linux_amd64 등)를 쓰면 Python 없이 설치할 수 있습니다.
# 이 스크립트는 소스에서 바로 설치할 때 쓰는 경로입니다.

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "[오류] Python 3 가 필요합니다."
    echo "       Python 없이 설치하려면 Releases 의 patcher 바이너리를 사용하세요."
    exit 1
fi

exec "$PYTHON" "$SCRIPT_DIR/tools/apply_patch.py" "$@"
