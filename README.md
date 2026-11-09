## ***Developed by Vũ Quang Đại / <QDai.Dev08@gmail.com>***
 > [!IMPORTANT]
> This software was built by me, at no cost and without outside support. Please respect the effort behind it.
> **Do not copy the code and pass it off as your own**, e.g. by replacing **Author & Developed by: Vu Quang Dai** with your name. It is open source and you may modify it, but credit is required.

- ✍️ ~99% hand-written; the remaining ~1% used AI only to simplify the code
- ⏱️ Many mistakes and countless hours went into getting it right
- 🎯 I stopped at this version, due to lack of funding and time constraints.

***If this project helps you, consider donating:***

<p align="center">
  <img src="https://github.com/user-attachments/assets/e44b917f-01d5-4df4-af07-17703e9b553f" alt="BIDV QR" width="200">
  <img src="https://github.com/user-attachments/assets/4dbc8764-1209-4233-87db-5cf78c9e8cf7" alt="PayPal Image" width="230"/> <br><br>

  <a href="https://www.paypal.com/paypalme/QDaiDev08">
    <img src="https://img.shields.io/badge/Donate-PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white" alt="PayPal">
  </a>
</p>


[![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-538CC9?style=for-the-badge&logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/intro)
[![Qt Designer](https://img.shields.io/badge/UI%20Design-Qt%20Designer-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://doc.qt.io/qt-6/qtdesigner-manual.html)
[![Pillow](https://img.shields.io/badge/Imaging-Pillow-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python-pillow.org/) <br>

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
* E. Uzun and H. T. Sencar, “[JpgScraper: An Advanced Carver for JPEG Files](https://doi.org/10.1109/TIFS.2019.2953382)”, IEEETransactions on Information Forensics and Security, 2019.
* E. Uzun and H. T. Sencar, “[Carving orphaned jpeg file fragments](https://www.researchgate.net/publication/275044127_Carving_Orphaned_JPEG_File_Fragments)”, IEEETransactions on Information Forensics and Security, vol. 10, no. 8, pp.1549–1563, 2015.

Thanks to the developers and communities behind these resources.

---

## 🚀 Running the Application
> [!TIP]
> Run the code directly with Python to get the latest version without waiting for the `.exe` release.
> Install any missing libraries. If you hit errors, fix them and send your suggestions back.
- **Build Executable**
```bash
pyinstaller --noconfirm --onefile --windowed --icon "resources/logo.ico" --name "RecoveryJpeg" --clean --log-level "INFO" --noupx --version-file "VERSION" "main.pyw"
```

- **Libs**
```
pip install PyQt6 pillow
```

- **Run**
```bash
python "main.pyw"
```




## Usage - 🎬 Demo Video
> [!NOTE]
> Email me for paid file-recovery requests (fees apply). Questions and issues will be answered as soon as possible.

<a href="https://youtu.be/Y71KwogXW8s">
  <img src="https://img.youtube.com/vi/Y71KwogXW8s/maxresdefault.jpg" width="400">
</a>
<a href="https://youtu.be/oKuoWYz6NP8">
  <img src="https://img.youtube.com/vi/oKuoWYz6NP8/maxresdefault.jpg" width="400">
</a>
