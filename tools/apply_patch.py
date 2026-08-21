# -*- coding: utf-8 -*-
"""Turing Complete 한국어 패치 설치 스크립트 (Python 버전).

install.sh / install.bat 이 호출한다. 배포용 단일 실행 파일은 patcher.go 를 쓴다.

하는 일
-------
1. 게임의 `translations/_ids_and_english.txt` 에서 현재 빌드의 id->영문 목록을 읽는다.
2. `translation_dict.json`(영문 원문 -> 한국어)을 대조해 `translations/Korean.txt` 를 만든다.
   ID 가 아니라 영문 원문으로 대조하므로 게임 업데이트로 ID 가 바뀌어도 살아남는다.
3. `asset/font/NotoSansSC_{Regular,Bold}.ttf` 를 한글 글리프가 있는 Noto Sans CJK SC 로
   교체한다(원본은 .orig 로 백업). 게임 동봉 폰트에는 한글 글리프가 없다.
"""
import argparse
import io
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tcloc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_SRC = os.path.join(ROOT, 'NotoSansCJK-SC-Korean.otf')
DICT_PATH = os.path.join(ROOT, 'translation_dict.json')

# 게임은 언어별로 폰트를 고른다: Japanese -> JP, Chinese (Traditional) -> TC, 그 외 -> SC.
# 한국어도 SC 로 떨어지므로 SC 두 벌을 교체한다. Noto Sans CJK SC 는 게임 동봉
# Noto Sans SC 의 상위 집합이라 중국어 간체 표시도 그대로 유지된다.
FONT_TARGETS = ('NotoSansSC_Regular.ttf', 'NotoSansSC_Bold.ttf')

STEAM_SUBPATH = os.path.join('steamapps', 'common', 'Turing Complete')


def is_game_dir(path):
    return (path and os.path.isdir(os.path.join(path, 'translations'))
            and os.path.isfile(os.path.join(path, 'asset', 'font', FONT_TARGETS[0])))


def steam_roots():
    home = os.path.expanduser('~')
    if sys.platform == 'win32':
        roots = [os.path.join(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'), 'Steam'),
                 os.path.join(os.environ.get('ProgramFiles', r'C:\Program Files'), 'Steam'),
                 os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Steam')]
    elif sys.platform == 'darwin':
        roots = [os.path.join(home, 'Library', 'Application Support', 'Steam')]
    else:
        roots = [os.path.join(home, '.local', 'share', 'Steam'),
                 os.path.join(home, '.steam', 'steam')]
    # libraryfolders.vdf 에 등록된 추가 라이브러리도 훑는다.
    for root in list(roots):
        vdf = os.path.join(root, 'steamapps', 'libraryfolders.vdf')
        if not os.path.isfile(vdf):
            continue
        try:
            text = io.open(vdf, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        for extra in re.findall(r'"path"\s+"([^"]+)"', text):
            extra = extra.replace(chr(92) * 2, chr(92))
            if extra not in roots:
                roots.append(extra)
    return roots


def find_game_dir():
    for root in steam_roots():
        candidate = os.path.join(root, STEAM_SUBPATH)
        if is_game_dir(candidate):
            return candidate
    return None


def load_reference(game_dir):
    """현재 빌드의 (섹션, id, 영문) 목록을 읽는다."""
    trans = os.path.join(game_dir, 'translations')
    primary = os.path.join(trans, '_ids_and_english.txt')
    if os.path.isfile(primary):
        return tcloc.parse(primary, id_prefixed=True), '_ids_and_english.txt'
    # 대체 경로: _debug.txt 는 본문을 X...X 로 감싸 둔다.
    fallback = os.path.join(trans, '_debug.txt')
    if os.path.isfile(fallback):
        entries = tcloc.parse(fallback)
        for e in entries:
            t = e.text
            if t.startswith('X'):
                t = t[1:]
            if t.endswith('X'):
                t = t[:-1]
            e.text = t.strip()
        return entries, '_debug.txt'
    return None, None


def build_translation(entries, mapping):
    out, hit = [], 0
    for e in entries:
        ko = mapping.get(tcloc.normalize(e.text))
        if ko:
            out.append(tcloc.Entry(e.section, e.id, ko))
            hit += 1
    return out, hit


def patch_fonts(game_dir, dry_run):
    font_dir = os.path.join(game_dir, 'asset', 'font')
    data = io.open(FONT_SRC, 'rb').read()
    for name in FONT_TARGETS:
        dest = os.path.join(font_dir, name)
        if not os.path.isfile(dest):
            print('[!] 폰트 대상 없음, 건너뜀: %s' % name)
            continue
        backup = dest + '.orig'
        if os.path.getsize(dest) == len(data):
            print('[=] %s 이미 패치됨' % name)
            continue
        if dry_run:
            print('[dry-run] %s 교체 예정 (백업: %s)' % (name, os.path.basename(backup)))
            continue
        if not os.path.exists(backup):
            shutil.copy2(dest, backup)
        with io.open(dest, 'wb') as fh:
            fh.write(data)
        print('[+] %s 교체 완료 (원본 -> %s)' % (name, os.path.basename(backup)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('game_dir', nargs='?')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-font', action='store_true')
    ap.add_argument('--out', help='Korean.txt 를 게임 폴더 대신 이 경로에 쓴다')
    args = ap.parse_args()

    game_dir = args.game_dir or find_game_dir()
    if not is_game_dir(game_dir):
        print('[오류] 올바른 게임 폴더가 아닙니다: %s' % game_dir)
        print('       translations/ 와 asset/font/NotoSansSC_Regular.ttf 가 있어야 합니다.')
        return 1
    print('[*] 게임 경로: %s' % game_dir)

    entries, source = load_reference(game_dir)
    if entries is None:
        print('[오류] 번역 대조용 원문 목록을 찾지 못했습니다.')
        print('       translations/_ids_and_english.txt 또는 _debug.txt 가 필요합니다.')
        return 1
    print('[*] 원문 목록: %s (%d개 항목)' % (source, len(entries)))

    mapping = json.load(io.open(DICT_PATH, encoding='utf-8'))['map']
    translated, hit = build_translation(entries, mapping)
    pct = hit * 100.0 / len(entries) if entries else 0.0
    print('[*] 사전 %d개와 대조 -> %d개 번역 (%.1f%%), 미번역 %d개'
          % (len(mapping), hit, pct, len(entries) - hit))

    dest = args.out or os.path.join(game_dir, 'translations', 'Korean.txt')
    if args.dry_run and not args.out:
        print('[dry-run] Korean.txt 쓰기 생략')
    else:
        tcloc.dump(translated, dest)
        print('[+] Korean.txt 저장: %s' % dest)

    if not args.no_font:
        patch_fonts(game_dir, args.dry_run)

    print('')
    print('게임 실행 후 Options > Language > 한국어 를 선택하세요.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
