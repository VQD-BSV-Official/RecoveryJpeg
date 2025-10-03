import struct

def main(jpeg_path):
    """
    Xác định kích thước MCU (Minimum Coded Unit) của tệp JPEG.
    Trả về tuple (width, height) của MCU tính bằng pixel.
    """
    try:
        with open(jpeg_path, 'rb') as f:
            data = f.read()
        
        # Tìm SOF marker (0xFFC0 hoặc 0xFFC2)
        i = 0
        while i < len(data) - 1:
            if data[i] == 0xFF and data[i+1] in (0xC0, 0xC2):  # SOF0 hoặc SOF2
                break
            i += 1
        
        if i >= len(data) - 1:
            raise ValueError("Không tìm thấy SOF marker trong tệp JPEG")
        
        # Di chuyển con trỏ đến phần dữ liệu của SOF
        i += 2
        # Đọc độ dài của đoạn SOF
        length = struct.unpack('>H', data[i:i+2])[0]
        i += 2
        # Bỏ qua precision (1 byte), height (2 bytes), width (2 bytes)
        i += 5
        # Đọc số lượng kênh màu
        num_components = data[i]
        i += 1
        
        # Đọc sampling factors cho từng kênh
        max_h = 1
        max_v = 1
        for _ in range(num_components):
            # Bỏ qua component ID (1 byte)
            # Đọc sampling factor (1 byte): 4 bit cao là H, 4 bit thấp là V
            sampling = data[i+1]
            h = (sampling >> 4) & 0x0F
            v = sampling & 0x0F
            max_h = max(max_h, h)
            max_v = max(max_v, v)
            i += 3  # Bỏ qua component ID, sampling, và quantization table ID
        
        # Tính kích thước MCU
        mcu_width = 8 * max_h
        mcu_height = 8 * max_v

        return mcu_width, mcu_height
    
    except Exception as e:
        print(f"error: {str(e)}")
        return None

main(input("Enter: "))