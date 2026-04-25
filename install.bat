@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo ========================================
echo   Turing Complete 한국어 패치 설치
echo ========================================
echo.

set SCRIPT_DIR=%~dp0

set "C0=%ProgramFiles(x86)%\Steam\steamapps\common\Turing Complete"
set "C1=%ProgramFiles%\Steam\steamapps\common\Turing Complete"
set "C2=%USERPROFILE%\AppData\Local\Steam\steamapps\common\Turing Complete"

set GAME_DIR=

for %%p in ("%C0%" "%C1%" "%C2%") do (
    if exist "%%~p\translations\English.txt" (
        set "GAME_DIR=%%~p"
        goto :found
    )
)

echo [!] Steam 경로를 자동으로 찾지 못했습니다.
echo     게임 폴더 경로를 직접 입력하세요:
set /p GAME_DIR="    경로: "

:found
if not exist "%GAME_DIR%\translations\English.txt" (
    echo [오류] 올바른 게임 폴더가 아닙니다.
    pause
    exit /b 1
)

echo [✓] 게임 경로: %GAME_DIR%
echo.

:: 1. 번역 파일 설치
copy /Y "%SCRIPT_DIR%Korean.txt" "%GAME_DIR%\translations\Korean.txt" >nul
echo [✓] Korean.txt 설치 완료
echo.

:: 2. PCK 폰트 패치
if not exist "%GAME_DIR%\Turing Complete.pck" (
    echo [!] PCK 파일을 찾을 수 없습니다. 폰트/언어 패치를 건너뜁니다.
    goto :done
)

echo [*] PCK 폰트 패치 중 (한글 렌더링 지원 추가)...
python "%SCRIPT_DIR%patch_font.py" "%GAME_DIR%\Turing Complete.pck" "%SCRIPT_DIR%NotoSansCJK-SC-Korean.otf"
if errorlevel 1 (
    echo [!] 폰트 패치 실패. Python이 설치되어 있는지 확인하세요.
)

:: 3. globals.gdc 패치 (언어 선택지에 '한국어' 추가)
echo [*] 언어 선택지 패치 중 (한국어 항목 추가)...
python "%SCRIPT_DIR%patch_globals.py" "%GAME_DIR%\Turing Complete.pck"
if errorlevel 1 (
    echo [!] globals.gdc 패치 실패. 게임 버전이 다를 수 있습니다.
)

:done
echo.
echo ==========================================
echo   설치 완료!
echo.
echo   게임 실행 후:
echo   Options ^> Language ^> 한국어 선택
echo   -^> 한국어로 표시됩니다
echo ==========================================
pause
