## ***Developed by Vũ Quang Đại / <QDai.Dev08@gmail.com>***
> [!Important]
> Please respect copyright, I created this software without any cost or support. ***DO NOT STEAL THE CODE AND MAKE IT YOURS, WHILE EVERYTHING IS BUILT BY ME***. For example: edit ***Author & Developed by: Vu Quang Dai*** to your name, I know open source you can edit everything, but I want respect for the effort I put in. **You can run the code directly using Python to update to the latest versions instead of waiting for the .exe release. Install any missing libraries, and if you encounter errors, please fix them and contribute your suggestions.** I coded 99% by hand, and the remaining 1% was done using AI to simplify the code. It took many mistakes to get the code right, and I spent hours at the computer. I didn't use AI for coding, so I cherish everything I've done. Therefore, you can donate to me.
> * ```You can contact me via gmail (email) to save the files you need. This will cost you a fee, thank you. If you have any problems or questions, I will reply as soon as possible. I will probably develop to version 2.0.0 and then stop. Lack of funding is getting me down and research is time consuming.```
> * <img src="https://github.com/user-attachments/assets/e44b917f-01d5-4df4-af07-17703e9b553f" alt="BIDV" width="200" style="max-width: 100%; margin: 0 auto;"> <br>
> * **Donate (Paypal)**: [Do consider donating or buying us a coffee](https://www.paypal.com/paypalme/QDaiDev08)


[![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-538CC9?style=for-the-badge&logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/intro) <br>

---

## 🖼️ Recover Your Photos
| Method | Description |
|---|---|
| 🧩 Extract Thumbnails | Extract JPEG thumbnail bytes `FFDB0084` or `FFDB0043` |
| 🛠️ Replace Headers | Use valid structure information from another file `FF DA 00` (SOS). |
| 🔗 Interlock MCU | Advanced recovery through MCU manipulation and reconstruction (Minimum Encoding Unit).

| Term | Explanation |
|------|-------------|
| **MCU** | Minimum Coded Unit. The fundamental processing unit in JPEG entropy coding. |
| **DCT** | Discrete Cosine Transform. Used to transform image data into frequency coefficients. |
| **Huffman Coding** | Entropy coding method used in standard DCT-based JPEG. |
| **Quantization** | Reduces DCT coefficient precision to achieve lossy compression. |
| **Entropy-Coded Data** | Compressed image data stored after an SOS marker. |
| **Restart Interval** | Number of MCUs between consecutive restart markers. |


| Short name | Bytes | Payload | Name | Comments |
|:---:|:---:|:---:|---|---|
| **SOI** | `FF D8` | `none` | Start Of Image | |
| **SOF0** | `FF C0` | `variable` | Start Of Frame (baseline DCT) | Indicates that this is a baseline DCT-based JPEG, and specifies the width, height, number of components, and component subsampling (e.g., 4:2:0). |
| **SOF2** | `FF C2` | `variable` | Start Of Frame (progressive DCT) | Indicates that this is a progressive DCT-based JPEG, and specifies the width, height, number of components, and component subsampling (e.g., 4:2:0). |
| **DHT** | `FF C4` | `variable` | Define Huffman Table(s) | Specifies one or more Huffman tables. |
| **DQT** | `FF DB` | `variable` | Define Quantization Table(s) | Specifies one or more quantization tables. |
| **DRI** | `FF DD` | `4 bytes` | Define Restart Interval | Specifies the interval between RSTn markers, in Minimum Coded Units (MCUs). This marker is followed by two bytes indicating the fixed size so it can be treated like any other variable size segment. |
| **SOS** | `FF DA` | `variable` | Start Of Scan | Begins a top-to-bottom scan of the image. In baseline DCT JPEG images, there is generally a single scan. Progressive DCT JPEG images usually contain multiple scans. This marker specifies which slice of data it will contain, and is immediately followed by entropy-coded data. |
| **RSTn** | `FF Dn`<br>`(n = 0..7)` | `none` | Restart | Inserted every *r* macroblocks, where *r* is the restart interval set by a DRI marker. Not used if there was no DRI marker. The low three bits of the marker code cycle in value from 0 to 7. |
| **APPn** | `FF En` | `variable` | Application-specific | For example, an Exif JPEG file uses an APP1 marker to store metadata, laid out in a structure based closely on TIFF. |
| **COM** | `FF FE` | `variable` | Comment | Contains a text comment. |
| **EOI** | `FF D9` | `none` | End Of Image | |


---

## 📚 References & Acknowledgements

This project was developed through independent research and learning from the following resources:

- [JpegRepair](https://github.com/dmahurin/jpegrepair)
- [JpegRecovery](https://github.com/euzun/jpeg-carver-csharp)
- [JpegDecomp](https://github.com/albmac/jpeg-decomp)
- [JPEGVisualRepairTool](https://github.com/albmac/JPEGVisualRepairTool)
- [JpegRepairShop](https://anderspedersen.net/jpegrepair/)
- [Wikipedia – JPEG](https://en.wikipedia.org/wiki/JPEG)

Thanks to the developers and communities behind these resources.

---

## ⚙️ Build Executable
```bash
pyinstaller --noconfirm --onefile --windowed --icon "resources/logo.ico" --name "RecoveryJpeg" --clean --log-level "INFO" --noupx --version-file "VERSION" "main.pyw"
```
## Usage - 🎬 Demo Video
<a href="https://youtu.be/oKuoWYz6NP8">
  <img src="https://img.youtube.com/vi/oKuoWYz6NP8/maxresdefault.jpg" width="600">
</a>
