# -*- coding: utf-8 -*-
r"""Turing Complete 번역 파일(.txt) 파서/직렬화기.

파일 형식
---------
    === <섹션 경로> ===

    $<id>* <본문>                  # 한 줄 본문
    $<id>*
    <본문 첫 줄>                    # 여러 줄 본문
    <본문 둘째 줄>

줄 첫머리의 `#` 는 뒤따르는 항목에 붙는 주석이며 본문이 아니다. 본문에 들어가는
리터럴 `#` 는 `\#` 로 이스케이프되므로 그대로 둔다.

`_ids.txt` / `_ids_and_english.txt` 처럼 게임이 생성한 참조 파일은 본문 앞에
id 가 한 번 더 붙는다(`$123* 123 Output`). 이 경우 id_prefixed=True 로 파싱한다.
"""
import io
import re

SECTION_RE = re.compile(r'^=== (.*) ===\s*$')
ENTRY_RE = re.compile(r'^\$(\d+)\*(.*)$')
COMMENT_RE = re.compile(r'^#')


class Entry:
    __slots__ = ('section', 'id', 'text')

    def __init__(self, section, id_, text):
        self.section, self.id, self.text = section, id_, text


def parse(path, id_prefixed=False):
    """번역 파일을 Entry 리스트로 읽는다. 파일 순서를 그대로 유지한다."""
    entries, section, cur_id, buf = [], None, None, []

    def flush():
        if cur_id is None:
            return
        text = '\n'.join(buf).strip('\n').strip()
        if id_prefixed:
            text = re.sub(r'^' + cur_id + r'[ \t]?', '', text)
        entries.append(Entry(section, cur_id, text))

    with io.open(path, encoding='utf-8', errors='replace') as fh:
        for line in fh:
            line = line.rstrip('\n').rstrip('\r')
            if COMMENT_RE.match(line):
                continue
            m = SECTION_RE.match(line)
            if m:
                flush()
                cur_id, buf = None, []
                section = m.group(1)
                continue
            m = ENTRY_RE.match(line)
            if m:
                flush()
                cur_id, buf = m.group(1), [m.group(2).lstrip()]
            elif cur_id is not None:
                buf.append(line)
    flush()
    return entries


def dump(entries, path):
    """Entry 리스트를 게임이 읽는 형식으로 쓴다(LF, UTF-8)."""
    out, last_section = [], None
    for e in entries:
        if e.section != last_section:
            out.append('\n\n' if last_section is not None else '')
            out.append('=== %s ===\n\n' % e.section)
            last_section = e.section
        if '\n' in e.text:
            out.append('$%s*\n%s\n' % (e.id, e.text))
        else:
            out.append('$%s* %s\n' % (e.id, e.text))
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(''.join(out))


def normalize(text):
    """원문 대조용 정규화 — 줄 끝 공백과 앞뒤 여백만 제거한다."""
    return '\n'.join(l.rstrip() for l in text.strip().split('\n'))
