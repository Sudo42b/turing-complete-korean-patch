#!/usr/bin/env python3
"""globals.gdc 패치 스크립트 - 언어 선택지에 '한국어' 추가 (Français 대체)"""
import struct, sys, os

if len(sys.argv) < 2:
    print("Usage: patch_globals.py <pck_path>")
    sys.exit(1)

pck_path = sys.argv[1]
target_name = "res://main_scripts/globals.gdc"

if not os.path.exists(pck_path):
    print(f"[오류] PCK 파일 없음: {pck_path}")
    sys.exit(1)

with open(pck_path, "rb") as f:
    data = bytearray(f.read())

# PCK 파일 테이블 파싱
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
    print("[!] globals.gdc 엔트리를 찾지 못했습니다")
    sys.exit(1)

gdc_offset = struct.unpack_from('<Q', data, target_tbl_pos)[0]
gdc_size   = struct.unpack_from('<Q', data, target_tbl_pos + 8)[0]
gdc = bytearray(data[gdc_offset:gdc_offset + gdc_size])

# Français(9 bytes) → 한국어(9 bytes), French(6 bytes) → Korean(6 bytes)
francais = "Français".encode('utf-8')
hangugeo = "한국어".encode('utf-8')
french   = b"French"
korean   = b"Korean"

if len(francais) != len(hangugeo):
    print(f"[오류] 바이트 길이 불일치: Français={len(francais)}, 한국어={len(hangugeo)}")
    sys.exit(1)

pos_fr = gdc.find(francais)
pos_en = gdc.find(french)

if pos_fr == -1 or pos_en == -1:
    # 이미 패치됐는지 확인
    if gdc.find(hangugeo) != -1:
        print("[✓] globals.gdc 이미 패치됨 (한국어 선택지 존재)")
        sys.exit(0)
    print("[!] Français/French 문자열을 찾지 못했습니다 - 게임 버전이 다를 수 있습니다")
    sys.exit(1)

gdc[pos_fr:pos_fr + len(francais)] = hangugeo
gdc[pos_en:pos_en + len(french)]   = korean

# 변경된 GDC를 PCK 끝에 추가하고 파일 테이블 업데이트
new_offset = len(data)
data.extend(gdc)
struct.pack_into('<Q', data, target_tbl_pos,     new_offset)
struct.pack_into('<Q', data, target_tbl_pos + 8, len(gdc))

with open(pck_path, "wb") as f:
    f.write(data)
print("[✓] globals.gdc 패치 완료 - 언어 선택지에 '한국어' 추가됨")
