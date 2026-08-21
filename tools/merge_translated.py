# -*- coding: utf-8 -*-
"""번역을 채워 넣은 작업 파일을 translation_dict.json 에 반영한다.

사용법:
    python tools/merge_translated.py todo.txt [game_dir]

작업 파일은 `tools/report_missing.py` 가 만든 형식이며, 영문이 그대로 남아 있는
항목은 미번역으로 보고 건너뛴다. 사전 키는 ID 가 아니라 영문 원문이므로
게임 업데이트로 ID 가 바뀌어도 번역이 유지된다.
"""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tcloc
from apply_patch import DICT_PATH, find_game_dir, is_game_dir, load_reference


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('translated', help='번역을 채운 작업 파일')
    ap.add_argument('game_dir', nargs='?')
    args = ap.parse_args()

    game_dir = args.game_dir or find_game_dir()
    if not is_game_dir(game_dir):
        print('[오류] 올바른 게임 폴더가 아닙니다: %s' % game_dir)
        return 1

    entries, _ = load_reference(game_dir)
    if entries is None:
        print('[오류] translations/_ids_and_english.txt 를 찾지 못했습니다.')
        return 1
    english = {e.id: e.text for e in entries}

    payload = json.load(io.open(DICT_PATH, encoding='utf-8'))
    mapping = payload['map']
    before = len(mapping)

    added = updated = skipped = unknown = 0
    for e in tcloc.parse(args.translated):
        en = english.get(e.id)
        if en is None:
            unknown += 1
            continue
        if not e.text or tcloc.normalize(e.text) == tcloc.normalize(en):
            skipped += 1
            continue
        key = tcloc.normalize(en)
        if key in mapping:
            if mapping[key] != e.text:
                updated += 1
        else:
            added += 1
        mapping[key] = e.text

    payload['entry_count'] = len(mapping)
    with io.open(DICT_PATH, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=0, sort_keys=True)
        fh.write('\n')

    print('[+] 신규 %d개, 수정 %d개' % (added, updated))
    print('[*] 영문 그대로라 건너뜀: %d개' % skipped)
    if unknown:
        print('[!] 현재 빌드에 없는 ID: %d개 (무시함)' % unknown)
    print('[+] 사전 %d -> %d개: %s' % (before, len(mapping), os.path.relpath(DICT_PATH)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
