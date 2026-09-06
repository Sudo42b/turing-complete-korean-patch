# Turing Complete 한국어 패치

Turing Complete 게임의 비공식 한국어 번역 패치입니다.

> **현재 번역률: 1,997 / 2,028 항목 (98.5%)** — 2026-09-06 빌드(Steam buildid `25036510`) 기준
> 남은 31개는 `ALU`, `r0`, `FPS`, `Mod 4` 같은 식별자·약어와 수식이라 영문을 그대로 둡니다.
> 자세한 내용은 [번역 현황](#번역-현황) 참고.

> **지원 버전:** 2026-08-17 빌드(Steam buildid `24685975`) 이후
> 그 이전 Godot 엔진 빌드는 지원하지 않습니다.

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

설치 후 게임에서 **Options → Language → 한국어** 를 선택하세요.

---

## 패치 내용

| 대상 | 하는 일 |
|---|---|
| `translations/Korean.txt` | 설치 시점에 생성. 게임이 배포한 원문 목록과 대조해 번역을 채운다 |
| `asset/font/NotoSansSC_Regular.ttf`<br>`asset/font/NotoSansSC_Bold.ttf` | 한글 글리프가 있는 Noto Sans CJK SC 로 교체 (원본은 `.orig` 로 백업) |

게임에 내장된 언어 목록에 **한국어(`ko`)가 이미 정식으로 들어 있어서**, 언어 선택지를
건드리는 패치는 필요 없습니다.

### 폰트를 왜 교체하나

게임은 언어에 따라 CJK 폰트를 고릅니다 — `Japanese` → JP, `Chinese (Traditional)` → TC,
**그 외 전부 → SC**. 한국어도 SC 로 떨어지는데, 동봉된 `Noto Sans SC` 에는 한글 글리프가
없어서 한국어를 선택하면 글자가 전부 두부(□)로 나옵니다.

교체용 `Noto Sans CJK SC` 는 동봉 폰트의 **상위 집합**(한자 전부 + 한글 + 가나)이라
중국어 간체 표시는 그대로 유지됩니다.

> 렌더러는 Dear ImGui 1.92.6 + stb_truetype 이며 CFF/OTF 를 파싱하므로,
> `.ttf` 이름으로 OTF 를 넣어도 정상 동작합니다.

---

## 동작 원리 — 왜 ID 를 박아두지 않나

게임의 번역 ID(`$48843089545173*`)는 **영문 원문의 해시**입니다. 원문이 한 글자라도
바뀌거나 로컬라이제이션 네임스페이스가 개편되면 ID 가 통째로 갈립니다. 실제로
2026-08-17 업데이트에서 다음이 벌어졌습니다:

| | 이전 (2026-08-03 빌드) | 현재 |
|---|---|---|
| 섹션 네임스페이스 | `trans/`, `components/`, `levels/`, `rpg/` | `campaign/`, `presenter/`, `asset/`, `model/` |
| 섹션 수 | 897 | 547 |
| 항목 수 | 1,719 | 2,048 |
| 겹치는 섹션 | — | **0개** |

그래서 이 패처는 `Korean.txt` 를 통째로 들고 다니지 않습니다. 대신:

1. `translation_dict.json` — **영문 원문 → 한국어** 사전을 내장한다
2. 설치할 때 게임의 `translations/_ids_and_english.txt` 에서 **현재 빌드의 ID ↔ 영문**을 읽는다
3. 영문 원문으로 대조해 그 자리에서 `Korean.txt` 를 생성한다

원문이 그대로면 ID 가 바뀌어도 번역이 살아남습니다. 게임 업데이트 후에는 패처만 다시
실행하면 됩니다.

---

## 번역 현황

```
전체 2,028 항목 (2026-09-06 빌드)
├─ 번역됨  1,997 (98.5%)
└─ 미번역     31 (1.5%)  — 총 295자, 전부 식별자/약어/수식
   ├─ campaign  21   ALU, LSR, ASR, r0~r5, X, Y, Mod 4, Overture, RNG 수식 …
   ├─ model      7   IO, Verilog, {size} KB …
   └─ presenter  3   FPS, ALU, {size} GB
```

2026-08-17 업데이트에서 로컬라이제이션 시스템이 개편되며 번역 대상 문자열이 통째로
교체됐습니다. 구 번역 2,161개 중 현재 빌드에 그대로 대응된 것은 339개뿐이라, 나머지
1,672개 항목을 새로 번역했습니다.

`legacy/Korean_legacy.txt` 에 구 빌드용 번역 원본이 보존돼 있습니다. 지금은 쓰이지
않는 항목도 원문이 다시 등장하면 사전에서 자동으로 되살아납니다.

### 서식 무결성

번역문에는 게임이 런타임에 치환·렌더링하는 조각이 그대로 남아 있어야 합니다:

| 종류 | 예 | 비고 |
|---|---|---|
| 치환 자리 | `{cycles_left}`, `{size}` | 이름까지 원문과 같아야 함 |
| 어셈블리 피연산자 | `%a`, `%value` | |
| 신호 토큰 | `[T]` `[F]` `[Z]` | 게임이 특수 렌더링. **번역하면 깨짐** |
| BBCode | `[b]`, `[color=#e49f44]` | |

구 번역이 신호 토큰을 `[ON]`/`[OFF]`/`[ANY]` 로 옮겨 적어 둔 것을 되돌렸습니다.
`tools/lint_dict.py` 로 검사하고 `--fix` 로 교정할 수 있으며, CI에서도 검증합니다.

---

## 번역 기여하기

```bash
# 1. 미번역 목록 뽑기 (게임 폴더는 자동 탐지)
python tools/report_missing.py -o todo.txt

# 2. todo.txt 의 영문 자리에 한국어를 채운다
#    형식:  $48843089545173* 여기에 번역
#    여러 줄이면 $id* 다음 줄부터 본문

# 3. 사전에 반영
python tools/merge_translated.py todo.txt

# 4. 서식 검사 후 적용
python tools/lint_dict.py
python tools/apply_patch.py
```

번역하지 않고 영문 그대로 둔 항목은 자동으로 건너뜁니다. 일부만 채워서 여러 번 나눠
반영해도 됩니다.

---

## 게임패드로 플레이하기 (Steam Input)

게임은 패드를 지원하지 않지만, `steam-input/` 의 Steam Input 레이아웃을 쓰면 패드 입력을
마우스·키보드로 바꿔 플레이할 수 있습니다. 게임 파일은 건드리지 않습니다.
설치와 조작법은 [steam-input/README.md](steam-input/README.md) 를 보세요.

---

## 저장소 구성

```
patcher.go              배포용 단일 실행 파일 (사전 + 폰트 내장)
translation_dict.json   영문 원문 -> 한국어 사전 (2,552개)
NotoSansCJK-SC-Korean.otf   한글 글리프 포함 교체용 폰트

tools/
  tcloc.py              게임 번역 파일 파서/직렬화기
  apply_patch.py        설치 (install.sh / install.bat 이 호출)
  build_dict.py         legacy 번역 -> 사전 재생성
  report_missing.py     미번역 작업 목록 추출
  merge_translated.py   번역한 작업 파일을 사전에 반영
  lint_dict.py          사전 서식 무결성 검사 (--fix 로 교정)

steam-input/
  controller_xboxone_turing_complete_ko.vdf   Steam Input 게임패드 레이아웃
  README.md             설치·조작법

legacy/
  Korean_legacy.txt     구 빌드용 번역 원본 2,161개 (사전 생성 소스)
  _ids_legacy.txt       구 빌드의 ID -> 영문 원문 목록
```

소스에서 바로 설치하려면 `install.bat`(Windows) / `install.sh`(Linux·macOS) 를 쓰세요.
Python 3 가 필요합니다. 릴리즈 바이너리는 아무것도 설치할 필요가 없습니다.

---

## 제거 방법

```bash
./patcher_linux_amd64 -restore        # 또는 patcher_windows_amd64.exe -restore
```

원본 폰트를 `.orig` 백업에서 되돌리고 `translations/Korean.txt` 를 삭제합니다.
Steam의 **게임 파일 무결성 검증**으로도 복구됩니다.

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

## 게임 업데이트 후

폰트 교체는 게임 업데이트 시 초기화됩니다. 번역 ID 도 바뀔 수 있습니다.
**패처를 다시 실행하면 둘 다 현재 빌드에 맞춰 다시 적용됩니다.**
