def decode_jpeg(input_path, output_path):
    import os

    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Tìm vị trí của marker SOS: FF DA
    sos_marker = b'\xFF\xDA'
    sos_pos = data.find(sos_marker)
    
    if sos_pos == -1:
        raise ValueError("Không tìm thấy marker SOS (FF DA) trong file JPEG!")
    
    # Bắt đầu từ sau SOS + 12 byte
    start_pos = sos_pos + 2 + 12  # +2 vì FF DA chiếm 2 byte
    payload = data[start_pos:]
    
    # Xử lý payload: nếu gặp FF thì thay byte tiếp theo thành 00
    result = bytearray()
    i = 0
    while i < len(payload):
        if payload[i] == 0xFF:
            result.append(0xFF)
            # Kiểm tra xem có còn byte tiếp theo không
            if i + 1 < len(payload):
                result.append(0x00)  # Thay byte sau FF thành 00
                i += 2  # Bỏ qua cả FF và byte sau
            else:
                result.append(0xFF)  # Nếu FF ở cuối file
                break
        else:
            result.append(payload[i])
            i += 1
    
    # Ghi lại file: phần đầu đến trước start_pos + payload đã xử lý
    with open(output_path, 'wb') as f:
        f.write(data[:start_pos])
        f.write(result)

# Sử dụng:
# import os

# file_inp = input("Enter: ")
# process_jpeg(file_inp, os.path.splitext(file_inp)[0] + "_decode.jpg" )