#!/bin/bash
# Turing Complete 한국어 패치 설치 스크립트 (Linux / macOS)

echo "========================================"
echo "  Turing Complete 한국어 패치 설치"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Steam 경로 자동 감지
CANDIDATES=(
    "$HOME/.local/share/Steam/steamapps/common/Turing Complete"
    "$HOME/.steam/steam/steamapps/common/Turing Complete"
    "$HOME/Library/Application Support/Steam/steamapps/common/Turing Complete"
)

GAME_DIR=""
for path in "${CANDIDATES[@]}"; do
    if [ -f "$path/translations/English.txt" ]; then
        GAME_DIR="$path"
        break
    fi
done

if [ -z "$GAME_DIR" ]; then
    echo "[!] Steam 경로를 자동으로 찾지 못했습니다."
    echo "    게임 폴더 경로를 직접 입력하세요 (translations 상위 폴더):"
    read -rp "    경로: " GAME_DIR
fi

if [ ! -f "$GAME_DIR/translations/English.txt" ]; then
    echo "[오류] 올바른 게임 폴더가 아닙니다: $GAME_DIR"
    exit 1
fi

echo "[✓] 게임 경로: $GAME_DIR"
echo ""

PCK="$GAME_DIR/Turing Complete.pck"

# 1. 번역 파일 설치
cp "$SCRIPT_DIR/Korean.txt" "$GAME_DIR/translations/Korean.txt" && echo "[✓] Korean.txt 설치 완료"
echo ""

# 2. PCK 폰트 패치 (한글 렌더링 지원)
echo "[*] PCK 폰트 패치 중 (한글 렌더링 지원 추가)..."
if [ ! -f "$PCK" ]; then
    echo "[!] PCK 파일을 찾을 수 없습니다. 폰트 패치를 건너뜁니다."
else
    python3 "$SCRIPT_DIR/patch_font.py" "$PCK" "$SCRIPT_DIR/NotoSansCJK-SC-Korean.otf"
    if [ $? -ne 0 ]; then
        echo "[!] 폰트 패치 실패. Python이 설치되어 있는지 확인하세요."
    fi
fi

# 3. globals.gdc 패치 (언어 선택지에 '한국어' 추가)
echo "[*] 언어 선택지 패치 중 (한국어 항목 추가)..."
if [ -f "$PCK" ]; then
    python3 "$SCRIPT_DIR/patch_globals.py" "$PCK"
    if [ $? -ne 0 ]; then
        echo "[!] globals.gdc 패치 실패. 게임 버전이 다를 수 있습니다."
    fi
fi

echo ""
echo "=========================================="
echo "  설치 완료!"
echo ""
echo "  게임 실행 후:"
echo "  Options > Language > 한국어 선택"
echo "  → 한국어로 표시됩니다"
echo "=========================================="
