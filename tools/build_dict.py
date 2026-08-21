# -*- coding: utf-8 -*-
"""구 번역(legacy/Korean_legacy.txt)을 '영문 원문 -> 한국어' 사전으로 변환한다.

게임의 번역 ID는 영문 원문의 해시라서, 게임이 원문을 손대거나 로컬라이제이션
네임스페이스를 개편하면 ID가 통째로 바뀐다(2026-08-17 업데이트가 그랬다).
ID 대신 영문 원문을 키로 삼으면 그 개편을 건너뛸 수 있다.

사용법:
    python tools/build_dict.py [--ref <id->영문 참조파일> ...] [-o translation_dict.json]

참조 파일은 게임이 배포하는 `translations/_ids.txt` 나
`translations/_ids_and_english.txt` 형식(본문 앞에 id 가 한 번 더 붙는 형식)이다.
"""
import argparse
import collections
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tcloc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--korean', default=os.path.join(ROOT, 'legacy', 'Korean_legacy.txt'))
    ap.add_argument('--ref', action='append', default=None,
                    help='id->영문 참조 파일 (여러 번 지정 가능)')
    ap.add_argument('-o', '--output', default=os.path.join(ROOT, 'translation_dict.json'))
    args = ap.parse_args()

    refs = args.ref or [os.path.join(ROOT, 'legacy', '_ids_legacy.txt')]

    korean = {e.id: e.text for e in tcloc.parse(args.korean) if e.text}

    english = {}
    for ref in refs:
        if not os.path.exists(ref):
            print('[!] 참조 파일 없음, 건너뜀: %s' % ref)
            continue
        n = 0
        for e in tcloc.parse(ref, id_prefixed=True):
            if e.text and e.id not in english:
                english[e.id] = e.text
                n += 1
        print('[*] %s: id->영문 %d개' % (os.path.relpath(ref, ROOT), n))

    # 같은 영문에 여러 한국어가 붙은 경우 최빈값을 채택한다.
    votes = collections.defaultdict(collections.Counter)
    for id_, ko in korean.items():
        en = english.get(id_)
        if en:
            votes[tcloc.normalize(en)][ko] += 1

    mapping = {}
    conflicts = 0
    for en, counter in votes.items():
        if len(counter) > 1:
            conflicts += 1
        mapping[en] = counter.most_common(1)[0][0]

    payload = {
        'version': 1,
        'note': 'English source text -> Korean. Keyed by source text so that game '
                'updates which rewrite translation IDs do not invalidate the patch.',
        'entry_count': len(mapping),
        'map': mapping,
    }
    with io.open(args.output, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=0, sort_keys=True)
        fh.write('\n')

    unmatched = len(korean) - sum(counter.total() for counter in votes.values())
    print('[+] 한국어 항목 %d개 / 영문 대응 확보 %d개' % (len(korean), len(korean) - unmatched))
    print('[+] 사전 %d개 (원문 중복 %d건은 최빈 번역 채택)' % (len(mapping), conflicts))
    print('[+] 영문 원문을 못 찾아 사전에 못 들어간 번역: %d개' % unmatched)
    print('[+] 저장: %s' % os.path.relpath(args.output, ROOT))


if __name__ == '__main__':
    main()
