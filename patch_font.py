#!/usr/bin/env python3
"""PCK 폰트 패치 스크립트 (Windows용 install.bat에서 호출)"""
import struct, sys, os

if len(sys.argv) < 3:
    print("Usage: patch_font.py <pck_path> <font_path>")
    sys.exit(1)

pck_path = sys.argv[1]
new_font_path = sys.argv[2]
target_name = "res://fonts/NotoSansSC-Regular.otf"

if not os.path.exists(pck_path):
    print(f"[오류] PCK 파일 없음: {pck_path}")
    sys.exit(1)

if not os.path.exists(new_font_path):
    print(f"[오류] 폰트 파일 없음: {new_font_path}")
    sys.exit(1)

with open(new_font_path, "rb") as f:
    new_font = f.read()

with open(pck_path, "rb") as f:
    data = bytearray(f.read())

HEADER_SIZE = 4 + 4 + 4 + 4 + 4 + 64
file_count = struct.unpack_from('<I', data, HEADER_SIZE)[0]
offset = HEADER_SIZE + 4
target_tbl_pos = None

for _ in range(file_count):
    plen = struct.unpack_from('<I', data, offset)[0]
    offset += 4
    path = data[offset:offset+plen].decode('utf-8', errors='replace').rstrip('\x00')
    offset += plen
    if path == target_name:
        target_tbl_pos = offset
    offset += 32

if target_tbl_pos is None:
    print("[!] NotoSansSC 엔트리를 찾지 못했습니다")
    sys.exit(0)

cur_size = struct.unpack_from('<Q', data, target_tbl_pos+8)[0]
if cur_size == len(new_font):
    print("[✓] PCK 폰트 이미 패치됨")
    sys.exit(0)

new_offset = len(data)
data.extend(new_font)
struct.pack_into('<Q', data, target_tbl_pos,   new_offset)
struct.pack_into('<Q', data, target_tbl_pos+8, len(new_font))

with open(pck_path, "wb") as f:
    f.write(data)
print("[✓] PCK 폰트 패치 완료")
