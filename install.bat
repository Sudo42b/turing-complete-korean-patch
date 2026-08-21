@echo off
chcp 65001 >nul
setlocal

rem Turing Complete 한국어 패치 설치 스크립트 (Windows)
rem
rem 릴리즈 바이너리(patcher_windows_amd64.exe)를 쓰면 Python 없이 설치할 수 있습니다.
rem 이 스크립트는 소스에서 바로 설치할 때 쓰는 경로입니다.

set "SCRIPT_DIR=%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [오류] Python 3 가 필요합니다.
    echo        Python 없이 설치하려면 Releases 의 patcher_windows_amd64.exe 를 사용하세요.
    pause
    exit /b 1
)

python "%SCRIPT_DIR%tools\apply_patch.py" %*
set "RC=%ERRORLEVEL%"

pause
exit /b %RC%
