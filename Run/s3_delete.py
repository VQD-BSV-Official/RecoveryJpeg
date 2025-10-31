import re
from pathlib import Path

OFFSET_RE = re.compile(r'0x([0-9A-Fa-f]+)\.(\d+)')

def parse_offsets_from_text(text):
    """Trả về danh sách offset (int) theo thứ tự xuất hiện."""
    offsets = []
    for m in OFFSET_RE.finditer(text):
        hexpart, post = m.group(1), int(m.group(2))
        val = int(hexpart, 16) + post
        offsets.append(val)
    return offsets

def make_ranges_from_offsets(offsets):
    """Lấy cặp (0-1, 2-3, ...) và trả về danh sách (start,end) với start<=end.
       Nếu lẻ 1 offset => bỏ offset cuối."""
    pairs = []
    n = (len(offsets) // 2) * 2
    for i in range(0, n, 2):
        a, b = offsets[i], offsets[i+1]
        if a <= b:
            pairs.append((a, b))
        else:
            pairs.append((b, a))
    # hợp nhất các range (nếu overlap hoặc kề nhau)
    if not pairs:
        return []
    pairs.sort()
    merged = []
    cur_s, cur_e = pairs[0]
    for s,e in pairs[1:]:
        if s <= cur_e + 1:
            cur_e = max(cur_e, e)
        else:
            merged.append((cur_s, cur_e))
            cur_s, cur_e = s, e
    merged.append((cur_s, cur_e))
    return merged

def remove_ranges_from_file(in_path, out_path, ranges):
    """Xóa các ranges (list of (start,end) inclusive) từ file in_path -> out_path.
       Thực hiện bằng cách đọc file nguyên vẹn (hiệu quả cho hầu hết trường hợp)."""
    if not ranges:
        # Path(in_path).replace(out_path)
        shutil.copy(in_path, out_path)
        print("Không có range nào để xóa — copy file gốc.")
        return
    data = Path(in_path).read_bytes()
    size = len(data)
    # kiểm tra range nằm trong file
    for s,e in ranges:
        if s < 0 or e >= size:
            raise ValueError(f"Range ({s},{e}) ngoài kích thước file ({size} bytes).")
    out = bytearray()
    prev = 0
    for s,e in ranges:
        out.extend(data[prev:s])
        prev = e + 1
    out.extend(data[prev:])
    Path(out_path).write_bytes(bytes(out))
    removed = size - len(out)
    print('Done')
    # print(f"Hoàn tất. Kích thước trước: {size} bytes, sau: {len(out)} bytes. Đã xóa {removed} bytes.")

def delete_mcu(in_file, out_file, lst):
    # --- Cách dùng ---
    # 1) Nếu bạn có văn bản offsets trong 1 file txt (ví dụ offsets.txt), dùng:
    #    text = Path("offsets.txt").read_text(encoding="utf-8")
    # 2) Hoặc bạn có sẵn string (ví dụ trực tiếp dán vào script)
    # sample_text = """/// MCU 1745 (125,10) (0x27E9C.2)        \\\\\\\\
# /// MCU 2089 (145,12) (0x2C05D.4)""" \\\\\\\\
    # Thay sample_text bằng nội dung file nếu cần:
    # sample_text = Path("offsets.txt").read_text(encoding="utf-8")
    sample_text = "\n".join(lst)
    # print(sample_text)
    offsets = parse_offsets_from_text(sample_text)
    # print("Offsets (decimal):", offsets)
    ranges = make_ranges_from_offsets(offsets)
    # print("Ranges (to remove):", ranges)

    # Đường dẫn file ảnh gốc và file kết quả
    # in_file = "F1_v1.jpg"
    # out_file = "a_fixed.jpg"
    remove_ranges_from_file(in_file, out_file, ranges)
