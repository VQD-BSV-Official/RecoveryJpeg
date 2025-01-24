def read_data(image):
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
                    print(f'>> {offset_start:X}x{offset_end:X}')
                    # self.uic.listWidget.addItem(f'{offset_start:X}x{offset_end:X}')

                    dump.seek(offset_end)
                    break

                else:
                    continue
    return list_offset