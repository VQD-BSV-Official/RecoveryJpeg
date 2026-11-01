#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jpeg_mcu_finder.py
Tìm offset hex của MCU (i,j) trong file JPEG
Tác giả: Grok (dựa trên yêu cầu của bạn)
Chạy: python jpeg_mcu_finder.py File_test.jpg 0 0
"""

import sys
import struct
from typing import Dict, List, Tuple

def find_marker(data: bytes, marker: bytes, start: int = 0) -> int:
    """Tìm marker (2 bytes) trong data từ vị trí start"""
    pos = data.find(marker, start)
    if pos == -1:
        raise ValueError(f"Marker {marker.hex()} not found")
    return pos

def parse_jpeg_header(jpeg_path: str) -> Dict:
    """Parse SOF, lấy kích thước ảnh, sampling, số MCU, offset SOS và tính avg_bytes_per_mcu"""
    with open(jpeg_path, 'rb') as f:
        data = f.read()

    # Tìm SOF (FF C0 - Baseline DCT)
    sof_pos = find_marker(data, b'\xff\xc0')
    length = struct.unpack('>H', data[sof_pos + 2:sof_pos + 4])[0]

    # Đọc các trường
    precision = data[sof_pos + 4]
    height = struct.unpack('>H', data[sof_pos + 5:sof_pos + 7])[0]
    width = struct.unpack('>H', data[sof_pos + 7:sof_pos + 9])[0]
    num_comp = data[sof_pos + 9]

    if num_comp == 0 or height == 0 or width == 0:
        raise ValueError("Invalid image dimensions or components")

    print(f"[INFO] Image: {width} x {height}, Components: {num_comp}, Precision: {precision}")

    # Đọc sampling factors
    sampling = []
    max_h = max_v = 0
    for i in range(num_comp):
        offset = sof_pos + 10 + 3 * i
        comp_id = data[offset]
        samp = data[offset + 1]
        qt_id = data[offset + 2]
        h = (samp >> 4) & 0x0F
        v = samp & 0x0F
        sampling.append((comp_id, h, v, qt_id))
        max_h = max(max_h, h)
        max_v = max(max_v, v)

    if max_h == 0 or max_v == 0:
        raise ValueError("Invalid sampling factors")

    mcu_w = max_h * 8
    mcu_h = max_v * 8
    num_mcu_w = (width + mcu_w - 1) // mcu_w
    num_mcu_h = (height + mcu_h - 1) // mcu_h
    total_mcus = num_mcu_w * num_mcu_h

    print(f"[INFO] MCU size: {mcu_w} x {mcu_h} pixels")
    print(f"[INFO] Total MCUs: {num_mcu_w} x {num_mcu_h} = {total_mcus}")
    print(f"[INFO] Sampling: {[(cid, f'{h}x{v}') for cid, h, v, _ in sampling]}")

    # Tìm SOS
    sos_pos = find_marker(data, b'\xff\xda', sof_pos)
    sos_length = struct.unpack('>H', data[sos_pos + 2:sos_pos + 4])[0]
    entropy_start = sos_pos + 2 + sos_length

    # Tìm EOI (End of Image)
    eoi_pos = data.find(b'\xff\xd9', entropy_start)
    if eoi_pos == -1:
        raise ValueError("EOI marker not found")
    
    entropy_data_size = eoi_pos - entropy_start
    print(f"[INFO] Entropy data starts at: 0x{entropy_start:06X}")
    print(f"[INFO] Entropy data size: {entropy_data_size} bytes")

    # Tìm DRI (nếu có)
    restart_interval = 0
    dri_pos = data.find(b'\xff\xdd', 0, sos_pos)
    if dri_pos != -1:
        restart_interval = struct.unpack('>H', data[dri_pos + 4:dri_pos + 6])[0]
        print(f"[INFO] Restart Interval (DRI): {restart_interval} MCUs")

    # Tính avg_bytes_per_mcu dựa trên kích thước thực tế
    if total_mcus > 0:
        if restart_interval > 0:
            # Trừ đi các byte marker restart (2 byte mỗi marker)
            num_restart_markers = (total_mcus - 1) // restart_interval
            adjusted_entropy_size = entropy_data_size - (num_restart_markers * 2)
            avg_bytes_per_mcu = adjusted_entropy_size / total_mcus
            print(f"[INFO] Adjusted entropy data size (without restart markers): {adjusted_entropy_size} bytes")
        else:
            avg_bytes_per_mcu = entropy_data_size / total_mcus
        
        print(f"[INFO] Calculated avg_bytes_per_mcu: {avg_bytes_per_mcu:.2f}")
    else:
        avg_bytes_per_mcu = 0
        print("[WARNING] Cannot calculate avg_bytes_per_mcu (total_mcus = 0)")

    return {
        'data': data,
        'width': width,
        'height': height,
        'mcu_w': mcu_w,
        'mcu_h': mcu_h,
        'num_mcu_w': num_mcu_w,
        'num_mcu_h': num_mcu_h,
        'entropy_start': entropy_start,
        'restart_interval': restart_interval,
        'sampling': sampling,
        'avg_bytes_per_mcu': avg_bytes_per_mcu
    }

def get_mcu_offset(info: Dict, mcu_i: int, mcu_j: int) -> int:
    """Trả về offset hex của MCU (i,j)"""
    num_mcu_w = info['num_mcu_w']
    target_idx = mcu_i + mcu_j * num_mcu_w
    total_mcus = num_mcu_w * info['num_mcu_h']

    if mcu_i >= num_mcu_w or mcu_j >= info['num_mcu_h']:
        raise ValueError(f"MCU ({mcu_i},{mcu_j}) out of range")

    # MCU (0,0): ngay sau SOS header
    if target_idx == 0:
        print(f"[RESULT] MCU ({mcu_i}, {mcu_j}) starts at: 0x{info['entropy_start']:06X}")
        return info['entropy_start']

    # Ước lượng cho MCU khác
    ri = info['restart_interval']
    avg_bytes = info['avg_bytes_per_mcu']
    
    if ri > 0:
        restarts_before = target_idx // ri
        estimated = info['entropy_start'] + int(target_idx * avg_bytes) + restarts_before * 2
        print(f"[ESTIMATE] MCU ({mcu_i}, {mcu_j}) ≈ 0x{estimated:06X} "
              f"(using DRI={ri}, avg {avg_bytes:.2f} bytes/MCU + {restarts_before*2} RST bytes)")
        return estimated
    else:
        estimated = info['entropy_start'] + int(target_idx * avg_bytes)
        print(f"[ESTIMATE] MCU ({mcu_i}, {mcu_j}) ≈ 0x{estimated:06X} "
              f"(no DRI, avg {avg_bytes:.2f} bytes/MCU)")
        return estimated

def main(jpeg_file, mcu_i, mcu_j):
    # if len(sys.argv) != 4:
    #     print("Usage: python jpeg_mcu_finder.py <jpeg_file> <mcu_i> <mcu_j>")
    #     print("Example: python jpeg_mcu_finder.py File_test.jpg 0 0")
    #     sys.exit(1)

    # jpeg_file = sys.argv[1]
    # try:
    #     mcu_i = int(sys.argv[2])
    #     mcu_j = int(sys.argv[3])
    # except ValueError:
    #     print("Error: MCU indices must be integers")
    #     sys.exit(1)

    try:
        print(f"[START] Analyzing {jpeg_file} ...")
        info = parse_jpeg_header(jpeg_file)
        offset = get_mcu_offset(info, mcu_i, mcu_j)
        print(f"\n[FINAL] MCU ({mcu_i}, {mcu_j}) hex offset: 0x{offset:06X}")
        
        return offset
        
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

# if __name__ == "__main__":
#     main()