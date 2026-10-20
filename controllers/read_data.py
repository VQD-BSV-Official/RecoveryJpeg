SOI_1, SOI_2, EOI = b'\xFF\xDB\x00\x84', b'\xFF\xDB\x00\x43', b'\xFF\xD9'
CHUNK = 1024

# Claude tối ưu lại
def check_end(filename):
    with open(filename, "r+b") as f:
        f.seek(-2, 2)                 # 2 byte cuối (2 = SEEK_END)
        if f.read(2) != EOI:
            f.write(EOI)              # thiếu FF D9 thì ghi nối vào cuối


def read_data(image):
    check_end(image)
    list_offset = []

    with open(image, 'rb') as dump:
        while buf := dump.read(CHUNK):
            pos = dump.tell() - len(buf)

            # Tìm điểm bắt đầu (ưu tiên 0084, không có thì 0043)
            idx = buf.find(SOI_1) if SOI_1 in buf else buf.find(SOI_2)
            if idx < 0:
                continue

            # Fix error (header FFC4)
            idx_2 = buf.find(b'\xFF\xC4')
            if 0 <= idx_2 < idx:
                idx = idx_2

            start = pos + idx
            dump.seek(start)

            # Tìm điểm cuối
            while buf_end := dump.read(CHUNK):
                idx_end = buf_end.find(EOI)
                if idx_end > 0:
                    end = dump.tell() - len(buf_end) + idx_end + 2
                    list_offset.append(f'{start:X}x{end:X}')
                    dump.seek(end)
                    break

    return list_offset