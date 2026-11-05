import re
from pathlib import Path

SOI_1, SOI_2, EOI = b'\xFF\xDB\x00\x84', b'\xFF\xDB\x00\x43', b'\xFF\xD9'
CHUNK = 1024
_OFFSET = re.compile(r'0x([0-9A-Fa-f]+)\.(\d+)')


def read_data(image):
    """Quét file, trả về list 'STARTxEND' (hex) của từng đoạn ảnh JPEG."""
    with open(image, "r+b") as f:  # thiếu FF D9 ở cuối thì ghi nối vào
        f.seek(-2, 2)
        if f.read(2) != EOI: f.write(EOI)

    offsets = []
    with open(image, 'rb') as dump:
        while buf := dump.read(CHUNK):
            pos = dump.tell() - len(buf)

            # Điểm bắt đầu: ưu tiên DQT 0084, không có thì 0043
            if (idx := buf.find(SOI_1)) < 0 and (idx := buf.find(SOI_2)) < 0: continue

            # Fix header FFC4
            if 0 <= (idx_2 := buf.find(b'\xFF\xC4')) < idx: idx = idx_2

            start = pos + idx
            dump.seek(start)

            # Điểm cuối
            while buf_end := dump.read(CHUNK):
                if (i := buf_end.find(EOI)) > 0:
                    end = dump.tell() - len(buf_end) + i + 2
                    offsets.append(f'{start:X}x{end:X}')
                    dump.seek(end)
                    break
    return offsets


def decode_jpeg(src, dst):
    """Escape mọi FF thành FF 00 trong scan data (sau SOS header)."""
    data = Path(src).read_bytes()
    if (sos := data.find(b'\xFF\xDA')) < 0: raise ValueError("Không tìm thấy marker SOS (FF DA)")
    start = sos + 14  # FF DA + 12 byte
    payload = re.sub(rb'\xFF.', b'\xFF\x00', data[start:], flags=re.DOTALL)
    if payload.endswith(b'\xFF'): payload += b'\xFF'  # FF lẻ cuối file: giữ hành vi cũ
    Path(dst).write_bytes(data[:start] + payload)


def delete_mcu(src, dst, lines):
    """Xoá byte từ offset MCU đầu đến offset MCU sau (inclusive).
    lines: các dòng log_mcu.txt dạng '... (0x27E9C.2)'; offset = hex + số sau dấu chấm."""
    offs = [int(h, 16) + int(p) for h, p in _OFFSET.findall("\n".join(lines))]
    ranges = sorted(tuple(sorted(offs[i:i + 2])) for i in range(0, len(offs) - 1, 2))  # offset lẻ cuối bị bỏ

    data = Path(src).read_bytes()
    if ranges and max(e for _, e in ranges) >= len(data):
        raise ValueError(f"Range ngoài kích thước file ({len(data)} bytes)")

    out, prev = bytearray(), 0
    for s, e in ranges:  # range chồng/kề nhau tự gộp: data[prev:s] rỗng khi s <= prev
        out += data[prev:s]
        prev = max(prev, e + 1)
    Path(dst).write_bytes(bytes(out + data[prev:]))


def jpeg_mcu(d: bytes):
    """(mcu_w, mcu_h) px từ sampling factor trong SOF; None nếu không parse được."""
    i, n = 2, len(d)
    while i + 4 <= n:
        if d[i] != 0xFF: i += 1; continue
        m = d[i + 1]
        if m == 0xFF: i += 1; continue
        if m in (0x01, 0xD8) or 0xD0 <= m <= 0xD7: i += 2; continue
        if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            hv = d[i + 11:i + 10 + 3 * d[i + 9]:3]
            return (8 * max(b >> 4 for b in hv), 8 * max(b & 15 for b in hv)) if hv else None
        if m == 0xDA: return None
        i += 2 + int.from_bytes(d[i + 2:i + 4], "big")
