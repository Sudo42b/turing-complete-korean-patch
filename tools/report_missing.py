# -*- coding: utf-8 -*-
"""아직 번역되지 않은 항목을 뽑아 번역 작업 목록을 만든다.

사용법:
    python tools/report_missing.py [game_dir] [-o work/todo.txt]

출력은 게임 번역 파일과 같은 형식이라, 영문 자리에 한국어를 채워 넣은 뒤
`tools/merge_translated.py` 로 사전에 반영하면 된다.
"""
import argparse
import collections
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tcloc
from apply_patch import DICT_PATH, find_game_dir, is_game_dir, load_reference


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('game_dir', nargs='?')
    ap.add_argument('-o', '--output', default='todo.txt')
    args = ap.parse_args()

    game_dir = args.game_dir or find_game_dir()
    if not is_game_dir(game_dir):
        print('[오류] 올바른 게임 폴더가 아닙니다: %s' % game_dir)
        return 1

    entries, source = load_reference(game_dir)
    if entries is None:
        print('[오류] translations/_ids_and_english.txt 를 찾지 못했습니다.')
        return 1

    mapping = json.load(io.open(DICT_PATH, encoding='utf-8'))['map']
    missing = [e for e in entries if tcloc.normalize(e.text) not in mapping]

    tcloc.dump(missing, args.output)

    by_prefix = collections.Counter(e.section.split('/')[0] for e in missing)
    total_chars = sum(len(e.text) for e in missing)
    print('[*] 원문 목록: %s (%d개 항목)' % (source, len(entries)))
    print('[*] 미번역 %d개 / 전체 %d개 (%.1f%% 남음)'
          % (len(missing), len(entries), len(missing) * 100.0 / len(entries)))
    print('[*] 미번역 원문 분량: 약 %s자' % format(total_chars, ','))
    print('')
    print('    영역별:')
    for prefix, n in by_prefix.most_common():
        print('      %-12s %5d개' % (prefix, n))
    print('')
    print('[+] 작업 목록 저장: %s' % args.output)
    print('    영문 자리에 한국어를 채운 뒤 tools/merge_translated.py 로 반영하세요.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
