import re

def decode_jpeg(input_path, output_path):
    with open(input_path, 'rb') as f:
        data = f.read()

    sos = data.find(b'\xFF\xDA')              # marker SOS
    if sos == -1:
        raise ValueError("Không tìm thấy marker SOS (FF DA) trong file JPEG!")

    start = sos + 14                          # FF DA (2 byte) + 12 byte
    payload = re.sub(rb'\xFF.', b'\xFF\x00', data[start:], flags=re.DOTALL)
    if payload.endswith(b'\xFF'):             # FF lẻ ở cuối file: giữ hành vi cũ (FF FF)
        payload += b'\xFF'

    with open(output_path, 'wb') as f:
        f.write(data[:start])
        f.write(payload)