# Steam Input 게임패드 레이아웃

Turing Complete 는 게임패드를 지원하지 않습니다. 이 레이아웃은 Steam Input 이 패드 입력을
마우스·키보드로 바꿔 주도록 만든 것이라 **게임 파일은 전혀 건드리지 않습니다.**
한국어 패치와 독립적으로 쓸 수 있습니다.

> 배선과 어셈블리 작성이 핵심인 게임이라 패드가 마우스·키보드만큼 빠를 수는 없습니다.
> 소파나 Steam Deck 에서 "플레이할 수 있게" 만드는 것이 목표입니다.

## 설치

`controller_xboxone_turing_complete_ko.vdf` 를 Steam 의 템플릿 폴더에 복사합니다.

| OS | 폴더 |
|---|---|
| Windows | `C:\Program Files (x86)\Steam\controller_base\templates\` |
| Linux | `~/.steam/steam/controller_base/templates/` |
| macOS | `~/Library/Application Support/Steam/controller_base/templates/` |
| Steam Deck | `~/.steam/steam/controller_base/templates/` (데스크톱 모드) |

그다음 Steam 에서:

1. 라이브러리 → Turing Complete → 컨트롤러 아이콘(또는 관리 → 컨트롤러 레이아웃)
2. **레이아웃 찾아보기 → 템플릿** 탭에서 `Turing Complete 게임패드 (한국어 패치)` 선택 → 적용

파일 이름이 `controller_xboxone_` 로 시작하지만 PlayStation, Switch Pro, Steam Deck 에서도
같은 레이아웃을 고를 수 있습니다(Steam 이 버튼을 대응해 줍니다).

## 조작

```
                 LB 축소                    RB 확대
                 LT 우클릭 (삭제·선택 해제)   RT 좌클릭 (배치·배선·드래그)

  왼쪽 스틱  라디얼 메뉴: 하위 메뉴 글자키 Q W E R T A S D F G Z X C V, 6, Esc
  L3         5 (커스텀 부품 메뉴)
  오른쪽 스틱 마우스 커서
  R3         마우스 가운데 버튼 (누른 채 스틱 이동 = 화면 이동)

  십자키 ↑ 1 비트 부품    → 2 워드 부품    ↓ 3 기타(메모리 등)    ← 4 입출력

  A  Space  부품 회전            B  Esc     뒤로 / 취소
  X  Ctrl+Z 되돌리기             Y  Shift   누른 채 RT 드래그 = 다중 선택

  View(뒤로)  Ctrl+C 복사        Menu(시작)  Ctrl+V 붙여넣기
```

### 부품 놓는 법

게임의 부품 단축키는 2단계입니다. 예를 들어 AND 게이트는 `1` → `W`, 8비트 덧셈기는 `2` → `E` → `Q` 입니다.

1. 십자키로 상위 메뉴를 고릅니다 (↑ 비트, → 워드, ↓ 기타, ← 입출력).
2. 화면에 뜬 하위 메뉴의 글자를 왼쪽 스틱 라디얼에서 고릅니다. 스틱을 해당 방향으로 밀었다 놓으면 입력됩니다.
3. 오른쪽 스틱으로 위치를 잡고 RT 로 놓습니다.

단축키는 게임 옵션에서 바꿀 수 있지만, 이 레이아웃은 **기본 단축키** 기준입니다.

## 확인이 필요한 항목

게임의 고정 단축키 중 일부는 기본값을 문서에서 확인하지 못해 관례적인 키로 넣었습니다.
게임 **옵션 → 조작(Control)** 탭에서 아래 항목의 실제 키를 확인하고, 다르면 게임 쪽 단축키를
아래 값으로 바꾸거나 Steam 레이아웃 편집기에서 버튼을 고치세요.

| 동작 | 레이아웃이 보내는 키 | 확인됨 |
|---|---|---|
| 회전 | Space | 예 (게임 내 팁) |
| 삭제 | 우클릭 | 예 (게임 내 툴팁) |
| 다중 선택 | Shift + 드래그 | 예 (게임 내 툴팁) |
| 부품 메뉴 | 1~6, Q~V | 예 (settings.txt) |
| 되돌리기 / 복사 / 붙여넣기 | Ctrl+Z / Ctrl+C / Ctrl+V | 아니오 (관례) |
| 확대 / 축소 | 마우스 휠 | 아니오 (관례) |
| 화면 이동 | 가운데 버튼 드래그 | 아니오 (관례) |
| 다시 실행, 사이클 실행 / 다음 / 리셋 | 미할당 | — |

미할당 동작은 Steam 레이아웃 편집기에서 남는 입력(예: 스틱 클릭 길게 누르기)에 직접 넣으면 됩니다.

## 어셈블리 코드 입력

코드 편집은 화상 키보드가 필요합니다. Steam 오버레이(기본 `Shift+Tab`, 패드에서는 Steam 버튼)의
키보드를 쓰거나, Steam Deck 에서는 `Steam + X` 로 띄울 수 있습니다.
