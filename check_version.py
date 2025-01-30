import requests

# URL rút gọn cho phiên bản phát hành mới nhất
url = "https://github.com/VQD-BSV-Official/RecoveryJpeg/releases/latest"

# Gửi yêu cầu GET đến URL
response = requests.get(url)

# Lấy phiên bản từ URL chuyển hướng
latest_version = response.url.split("/")[-1]

print(f"Phiên bản mới nhất: {latest_version}")
