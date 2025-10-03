def check_end(filename):
    with open(filename, "rb") as f:
        f.seek(-2, 2)  # nhảy tới 2 byte cuối (2 = SEEK_END)
        last2 = f.read(2)

    if last2 != b"\xFF\xD9":
        # print(f"{filename}: thiếu FF D9, thêm vào...")
        with open(filename, "ab") as f:  # ghi nối vào cuối
            f.write(b"\xFF\xD9")
    else:
        pass
        # print(f"{filename}: đã đúng.")



def read_data(image):
    check_end(image)

    with open(image, 'rb') as dump:
        list_offset = []
        while True: # Đọc file (image)
            pos = dump.tell()
            buf = dump.read(1024)
            if not buf: # Đọc đến hết
                break

            idx = buf.find(b'\xFF\xDB\x00\x84')
            if idx < 0: # Tìm 2 điểm bắt đầu
                idx = buf.find(b'\xFF\xDB\x00\x43')
                if idx < 0:
                    dump.seek(pos + 1024)
                    continue

            dump.seek(offset_start := pos + idx)

            while True:
                pos_end = dump.tell()
                buf_end = dump.read(1024)
                if not buf_end: # Đọc đến hết
                    break

                idx_end = buf_end.find(b'\xFF\xD9')
                if idx_end > 0: # Tìm điểm cuối
                    offset_end = pos_end + idx_end + 2

                    # Kết quả
                    list_offset.append(f'{offset_start:X}x{offset_end:X}')
                    # print(f'>> {offset_start:X}x{offset_end:X}')
                    # self.uic.listWidget.addItem(f'{offset_start:X}x{offset_end:X}')

                    dump.seek(offset_end)
                    break

                else:
                    continue

            if idx_end == -1:
                print("hi")
                    
    return list_offset