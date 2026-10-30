## ***Developed by Vũ Quang Đại / <QDai.Dev08@gmail.com>***
> [!Important]
> Please respect copyright, I created this software without any cost or support. ***DO NOT STEAL THE CODE AND MAKE IT YOURS, WHILE EVERYTHING IS BUILT BY ME***. For example: edit ***Author & Developed by: Vu Quang Dai*** to your name, I know open source you can edit everything, but I want respect for the effort I put in. **You can run the code directly using Python to update to the latest versions instead of waiting for the .exe release. Install any missing libraries, and if you encounter errors, please fix them and contribute your suggestions.** I coded 99% by hand, and the remaining 1% was done using AI to simplify the code. It took many mistakes to get the code right, and I spent hours at the computer. I didn't use AI for coding, so I cherish everything I've done. Therefore, you can donate to me.
> * ```You can contact me via gmail (email) to save the files you need. This will cost you a fee, thank you. If you have any problems or questions, I will reply as soon as possible. I will probably develop to version 2.0.0 and then stop. Lack of funding is getting me down and research is time consuming.```
> * <img src="https://github.com/user-attachments/assets/e44b917f-01d5-4df4-af07-17703e9b553f" alt="BIDV" width="200" style="max-width: 100%; margin: 0 auto;"> <br>
> * **Donate (Paypal)**: [Do consider donating or buying us a coffee](https://www.paypal.com/paypalme/QDaiDev08)


[![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-538CC9?style=for-the-badge&logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/intro) <br>


## 🖼️ Recover Your Photos
| Method | Description |
|---|---|
| 🧩 Thumbnail Extraction | Extract embedded JPEG thumbnails by locating image data between `FFDB` and `FFD9` markers where applicable. |
| 🛠️ Header Replacement | Attempt to reconstruct damaged JPEG headers using valid structural information from another file. |
| 🔗 MCU Concatenation | Advanced recovery through MCU (Minimum Coded Unit) manipulation and reconstructi
- 153605 is the number of bytes encoded at the beginning of the file. Different ransomware types have different encryption methods, but most ransomware with 4 characters at the end uses this encoding.


<img width="636" height="549" alt="image" src="https://github.com/user-attachments/assets/c2a167e6-a631-4445-9bca-d88b2e52081d" />


| Chroma Subsampling | MCU Size | Typical Cameras |
|---|---|---|
| **4:4:4** | 8 | Higher-end compacts, some DSLRs |
| **4:2:2** | 16 | Canon DSLRs (default JPEG) |
| **4:2:0** | 16 | Most phones, consumer cameras |


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
