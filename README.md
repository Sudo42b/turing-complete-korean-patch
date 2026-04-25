# Turing Complete 한국어 패치

Turing Complete 게임의 비공식 한국어 번역 패치입니다.  
총 **2,161개** 텍스트 항목을 한국어로 번역했습니다.

> **지원 버전:** 게임 `0.1059 Beta`  
> 다른 버전에서는 PCK 패치가 적용되지 않을 수 있습니다.

---

## 설치 방법

### Windows
1. [Releases](../../releases/latest) 에서 `patcher_windows_amd64.exe` 다운로드
2. 더블클릭하여 실행
3. Steam 경로가 자동으로 감지되지 않으면 직접 입력

### Linux
```bash
chmod +x patcher_linux_amd64
./patcher_linux_amd64
```

### macOS
```bash
# Intel Mac
chmod +x patcher_macos_amd64 && ./patcher_macos_amd64

# Apple Silicon (M1/M2/M3)
chmod +x patcher_macos_arm64 && ./patcher_macos_arm64
```
> 처음 실행 시 보안 경고가 뜨면: 시스템 설정 → 개인 정보 보호 및 보안 → "확인 없이 열기"

---

## 적용 방법

설치 후 게임에서:

**Options → Language → 한국어** 선택 → 한국어로 표시됩니다

---

## 무결성 검증 (권장)

릴리즈에 포함된 `checksums.sha256` 파일로 다운로드한 파일이 변조되지 않았는지 확인할 수 있습니다.

### Linux / macOS
```bash
# checksums.sha256 과 실행 파일을 같은 폴더에 놓고 실행
sha256sum -c checksums.sha256
```

### Windows (PowerShell)
```powershell
Get-FileHash patcher_windows_amd64.exe -Algorithm SHA256
# 출력된 해시값을 checksums.sha256 파일의 값과 비교
```

### GitHub Actions 빌드 증명 확인
이 패치의 바이너리는 GitHub Actions CI에서 소스코드를 직접 컴파일하여 생성됩니다.  
[Actions 탭](../../actions)에서 빌드 로그와 **Build Provenance Attestation**을 확인할 수 있습니다.

```bash
# GitHub CLI로 증명 검증 (선택사항)
gh attestation verify patcher_linux_amd64 --repo <owner>/<repo>
```

---

## 패치 내용

- `translations/Korean.txt` — 2,161개 한국어 번역 파일 추가
- PCK 폰트 패치 — 한글 렌더링 지원 (NotoSansCJK 폰트 교체)
- PCK globals 패치 — 언어 선택 메뉴에 '한국어' 항목 추가

> Python, .NET 등 별도 설치 불필요. 단일 실행 파일로 동작합니다.

---

## 제거 방법

Steam에서 **게임 파일 무결성 검증**을 실행하면 원본으로 복구됩니다.  
`translations/Korean.txt`는 직접 삭제해야 합니다.

## 게임 업데이트 후

PCK 패치는 게임 업데이트 시 초기화될 수 있습니다.  
패처를 다시 실행하면 됩니다 (번역 파일은 유지됩니다).
