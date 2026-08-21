# -*- coding: utf-8 -*-
"""번역 사전의 서식 무결성을 검사한다.

게임 텍스트에는 런타임에 치환되는 조각들이 섞여 있다. 이것들이 번역에서
빠지거나 바뀌면 문자열이 그대로 깨져 보인다:

* `{name}`  — 값 치환 자리
* `%name`   — 어셈블리 피연산자
* `[T]` `[F]` `[Z]` — 신호 상태 토큰 (게임이 특수 렌더링한다)
* `[b]` `[color=...]` 등 BBCode 태그

사용법:
    python tools/lint_dict.py            # 검사만
    python tools/lint_dict.py --fix      # 자동 교정 가능한 항목을 고친다

--fix 가 고치는 것:
  1. 구 번역이 `[T]`/`[F]` 를 옮겨 적은 `[ON]`/`[OFF]` 를 원래 토큰으로 되돌린다.
  2. 원문에 없는데 번역에만 붙은 장식 태그(`[i]`, `[center]`)를 떼어 낸다.
"""
import argparse
import collections
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tcloc
from apply_patch import DICT_PATH, find_game_dir, is_game_dir, load_reference

PLACEHOLDER_RE = re.compile(r'\{[^}\n]*\}')
OPERAND_RE = re.compile(r'%[A-Za-z_][A-Za-z_0-9]*')
TAG_RE = re.compile(r'\[/?[a-zA-Z][^\]\n]*\]')

# 구 번역이 게임의 특수 토큰을 한국어로 옮겨 적은 흔적. 이 토큰들은 게임이
# 직접 렌더링하므로 번역하면 문자열이 깨진 채 표시된다.
TOKEN_FIXES = (
    ('[ON]', '[T]'),
    ('[OFF]', '[F]'),
    ('[ANY]', '[Z]'),
    ('[명령어]', '[INSTRUCTION]'),
    ('[저장]', '[SAVE]'),
    ('[불러오기]', '[LOAD]'),
)

# 원문에 없는데 번역에만 붙은 경우 떼어 낼 장식 태그.
STRIPPABLE = ('i', 'center')


def check(entries, mapping):
    """(문제 유형 -> 건수, 상세 목록) 반환."""
    counts = collections.Counter()
    details = []
    for e in entries:
        ko = mapping.get(tcloc.normalize(e.text))
        if not ko:
            continue
        for name, rx in (('placeholder', PLACEHOLDER_RE),
                         ('operand', OPERAND_RE),
                         ('bbcode', TAG_RE)):
            # 원문이 `{{` 로 중괄호를 이스케이프하면 자리표시자 추출이 어긋난다.
            if name == 'placeholder' and '{{' in e.text:
                continue
            src, dst = sorted(rx.findall(e.text)), sorted(rx.findall(ko))
            if src == dst:
                continue
            counts[name] += 1
            details.append((name, e.section, e.id,
                            [x for x in src if src.count(x) > dst.count(x)],
                            [x for x in dst if dst.count(x) > src.count(x)]))
    return counts, details


def fix(mapping):
    token_fixed = strip_fixed = 0
    for key, val in list(mapping.items()):
        new = val
        for wrong, right in TOKEN_FIXES:
            if wrong in new and wrong not in key:
                new = new.replace(wrong, right)
                token_fixed += 1
        for tag in STRIPPABLE:
            open_tag, close_tag = '[%s]' % tag, '[/%s]' % tag
            if open_tag in new and open_tag not in key:
                new = new.replace(open_tag, '').replace(close_tag, '')
                strip_fixed += 1
        if new != val:
            mapping[key] = new
    return token_fixed, strip_fixed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('game_dir', nargs='?')
    ap.add_argument('--fix', action='store_true')
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()

    game_dir = args.game_dir or find_game_dir()
    if not is_game_dir(game_dir):
        print('[오류] 올바른 게임 폴더가 아닙니다: %s' % game_dir)
        return 1
    entries, _ = load_reference(game_dir)
    if entries is None:
        print('[오류] translations/_ids_and_english.txt 를 찾지 못했습니다.')
        return 1

    payload = json.load(io.open(DICT_PATH, encoding='utf-8'))
    mapping = payload['map']

    if args.fix:
        token_fixed, strip_fixed = fix(mapping)
        payload['entry_count'] = len(mapping)
        with io.open(DICT_PATH, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=0, sort_keys=True)
            fh.write('\n')
        print('[+] 신호 토큰 복원 %d건, 장식 태그 제거 %d건' % (token_fixed, strip_fixed))

    counts, details = check(entries, mapping)
    if not counts:
        print('[+] 서식 불일치 없음')
        return 0

    print('[!] 서식 불일치: %s' % dict(counts))
    if args.verbose:
        for name, section, id_, only_src, only_dst in details:
            print('  [%s] %s $%s' % (name, section, id_))
            if only_src:
                print('      원문에만:', only_src[:8])
            if only_dst:
                print('      번역에만:', only_dst[:8])
    else:
        print('    자세히 보려면 --verbose')
    return 0


if __name__ == '__main__':
    sys.exit(main())
