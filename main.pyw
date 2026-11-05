# /////////////////////////////////////////////
# >>> SYSTEM ⚙️ ──────────────────────────────
import sys, os, subprocess, binascii, shutil, time
from io import BytesIO
from pathlib import Path

# /////////////////////////////////////////////
# >>> THIRD-PARTY 👾 ─────────────────────────
from PIL import Image, ImageFile  # Image processing

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QShortcut, QKeySequence, QPixmap, QIcon, QImage, QPainter, QFontMetrics
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QListView,
)

# /////////////////////////////////////////////
# >>> CORE 🕵️ ───────────────────────────────
from controllers.jpeg_tools import read_data, decode_jpeg, delete_mcu, jpeg_mcu
from controllers.image_canvas import ImageCanvas

# /////////////////////////////////////////////
# >>> UI 💻 ──────────────────────────────────
from views.Sreen.GUI import Ui_MainWindow
from views.Widget.About import Ui_About
from views.Widget.Create import Ui_Create_New
from views.Widget.Edit_Image import Ui_Edit_Image




def _run(args, wait=True):
    si = subprocess.STARTUPINFO(); si.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # ẩn console
    return subprocess.run(args, startupinfo=si) if wait else subprocess.Popen(args, startupinfo=si)


def to_pixmap(raw):
    """JPEG bytes (đủ FFD8) -> QPixmap; fallback PIL cho ảnh lỗi/truncated."""
    pm = QPixmap()
    if pm.loadFromData(raw, "JPEG"): return pm
    try:
        img = Image.open(BytesIO(raw)).convert("RGB")
        w, h = img.size
        buf = img.tobytes()
        return QPixmap.fromImage(QImage(buf, w, h, 3 * w, QImage.Format.Format_RGB888))
    except Exception:
        return None


# ══════════════════════════════════════════ 🧩 CLASS 🧩 ════════════════════════════════════════════
# ════════════════════════════════════════════════════════════════════════════════════════════════════
class MainWindow:
    def __init__(self):
        self.main_win = QMainWindow()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self.main_win)


        required = ["JpegDecomp.exe", "JpegRepair.exe", "JpegRecovery.exe"]
        missing = [f for f in required if not (Path("tool") / f).is_file()]

        if missing:
            raise FileNotFoundError(
                "Missing tools:\n"
                + "\n".join(f"- {f}" for f in missing)
                + "\n\nPlease add missing files or rebuild via Git Submodules.\n\n"
                "Unavailable features:\n"
                "- Decode image\n"
                "- Insert/Delete Y, Cb, Cr\n"
                "- Auto Recover JPEG"
            )




        self.JPEG_HEADER = bytes.fromhex('FFD8FFE1007C45786966000049492A000800000003000E010200270000003200000012010300010000000100000031010200190000005A000000000000005265706169726564206279205175616E6720446169202020200000000000000000000009000000005265636F766572794A7065672000000000000000000000000000')
        self.MARKERS = (b"\xFF\xDB\x00\x84", b"\xFF\xDB\x00\x43")

        ImageFile.LOAD_TRUNCATED_IMAGES = True

        # //////////////////////////////////////////
        # //////////////////////////////////////////
        self.uic.splitter.setSizes([400, 125])
        self.uic.splitter_2.setSizes([220, 100])

        self._init_thumbnail()
        self._init_signals()
        
        # Value - N3T4_26
        self.image = ""
        self.start = self.end = 0
# ════════════════════════════════════════ 🧩 INIT CLASS🧩 ══════════════════════════════════════════
# ════════════════════════════════════════════════════════════════════════════════════════════════════
    def _init_thumbnail(self):
        u = self.uic

        u.listWidget.setViewMode(QListView.ViewMode.IconMode)
        u.listWidget.setFlow(QListView.Flow.LeftToRight)
        u.listWidget.setWrapping(True)
        u.listWidget.setResizeMode(QListWidget.ResizeMode.Adjust)
        u.listWidget.setMovement(QListView.Movement.Static)
        u.listWidget.setSpacing(12)

        # THAM SỐ: thay đổi nếu muốn thumbnail khác
        self.thumb_w = 89
        self.thumb_h = 89
        self.thumb_size = QSize(self.thumb_w, self.thumb_h)
        u.listWidget.setIconSize(self.thumb_size)

        # Tính chiều cao cho text (dựa vào font hiện tại)
        fm = QFontMetrics(u.listWidget.font())
        text_h = fm.height() + 4  # + padding nhỏ

        # Grid size = thumbnail + khoảng cho text + padding
        grid_w = self.thumb_w + 20
        grid_h = self.thumb_h + text_h + 18
        self.grid_size = QSize(grid_w, grid_h)
        u.listWidget.setGridSize(self.grid_size)


    def _init_signals(self):
        u = self.uic
        
        u.Decode.triggered.connect(self.decode_image)

        # Open File, Folder - N3T4_26
        u.Open_File.triggered.connect(self.open_file)
        u.Open_Folder.triggered.connect(self.open_folder)

        # Save File, Export Folder - N3T4_26
        u.Save.triggered.connect(self.save_file)
        u.Export.triggered.connect(self.export_folder)

        u.None_Hex.triggered.connect(self.none_Hex)
        u.x25805.triggered.connect(self.hex_x25805)
        u.RAW.triggered.connect(self.RAW)

        # Show Edit Image, About, Create New - N3T4_26
        u.Edit_Image.triggered.connect(self.show_image_editor)
        u.About.triggered.connect(self.show_about)
        u.Create_New.triggered.connect(self.show_Create_New)

        u.listWidget.itemClicked.connect(self.item_clicked)


    def add_image(self, item_off):
        # Parse offset hex - kiểu "0xSTARTxEND"
        self.start, self.end = (int(x, 16) for x in item_off.split('x'))

        with open(self.image, "rb") as f:
            f.seek(self.start)
            data = f.read(self.end - self.start)

        if pixmap := self.read_image(data):
            # Thumbnail vuông: scale giữ tỉ lệ, canh giữa trên nền trắng
            scaled = pixmap.scaled(self.thumb_w, self.thumb_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            thumb = QPixmap(self.thumb_w, self.thumb_h)
            thumb.fill(Qt.GlobalColor.white)  # đổi sang transparent nếu muốn

            painter = QPainter(thumb)
            painter.drawPixmap((self.thumb_w - scaled.width()) // 2,(self.thumb_h - scaled.height()) // 2, scaled)
            painter.end()

            item = QListWidgetItem(QIcon(thumb), f"{pixmap.width()}x{pixmap.height()}")
            item.setSizeHint(self.grid_size)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
            item.setToolTip(item_off)
            self.uic.listWidget.addItem(item)

# ══════════════════════════════════════════ 🧠 MAIN 🧠 ═════════════════════════════════════════════
# ════════════════════════════════════════════════════════════════════════════════════════════════════
    # Find marker - N24T1_25
    def main(self):
        if not self.image: return

        offsets = read_data(self.image)
        self.uic.textEdit.insertPlainText("\n     ✅ Open >> Read >> Found" if offsets else "\n     ❌ Open >> Read >> Not found")
        for offset in offsets:
            self.add_image(offset)
            

# ══════════════════════════════════════════ 🛰️ TOOLs 🛰️ ════════════════════════════════════════════
# ════════════════════════════════════════════════════════════════════════════════════════════════════
    # View image (label) - N3T9_25
    def view_label(self, label_width, label_height, pixmap):
        # Tạo QImage với kích thước của QLabel
        image = QImage(label_width, label_height, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)  # Nền trong suốt

        # Tính toán kích thước ảnh giữ tỷ lệ
        scaled_pixmap = pixmap.scaled(label_width, label_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        # Dùng QPainter để căn giữa ảnh trên QLabel
        painter = QPainter(image)
        x_offset = (label_width - scaled_pixmap.width()) // 2
        y_offset = (label_height - scaled_pixmap.height()) // 2
        painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
        painter.end()

        return image  


    def read_image(self, data):  # data không gồm SOI
        if (pm := to_pixmap(b"\xFF\xD8" + data)) is None: self.uic.textEdit.insertPlainText("...❌ - ReadImage")
        return pm

    # Click Item & View - N24T1_25
    def item_clicked(self, item):
        self.start, self.end = (int(x, 16) for x in item.toolTip().split('x'))

        with open(self.image, "rb") as f:
            f.seek(self.start)
            pixmap = self.read_image(f.read(self.end - self.start))

        if pixmap:
            label = self.uic.label
            label.setPixmap(QPixmap.fromImage(self.view_label(label.width(), label.height(), pixmap)))
            label.setFixedSize(label.size())
            label.setScaledContents(False)

# ══════════════════════════════════════════ 🛰️ TOOLs 🛰️ ════════════════════════════════════════════
# ════════════════════════════════════════════════════════════════════════════════════════════════════
    # Decode Image - N31T10_25 - OK have check error
    def decode_image(self):
        if self.image:
            decode_jpeg(self.image, os.path.splitext(self.image)[0] + "_decode.jpg")
            self.uic.textEdit.append("     ✅ Decode")
        else: self.uic.textEdit.append("     ❌ Can't decode")


# ════════════════════════════════════════════════════════════════════════════════════════════════════
# ════════════════════════════════════════════════════════════════════════════════════════════════════
    def _repaired(self, raw):
        """Gắn header chuẩn vào dữ liệu từ DQT đầu tiên; None nếu không có marker."""
        pos = [p for p in map(raw.find, self.MARKERS) if p >= 0]
        if not pos: return None
        return b"\xFF\xD8" + raw if raw[:2] == b"\xFF\xC4" else self.JPEG_HEADER + raw[min(pos):]  # FF D8 FF C4 giữ nguyên


    # Save File - N26T9_25
    def save_file(self):
        path = QFileDialog.getSaveFileName(None, "Save File", None, filter='JPEG files (*.JPG);; All files (*)')[0]
        if not (path and self.image and self.start):
            self.uic.textEdit.append("     ❌ Can't save"); return

        with open(self.image, "rb") as f:
            f.seek(self.start)
            raw = f.read(self.end - self.start)

        if (data := self._repaired(raw)) is None:
            self.uic.textEdit.append("     ❌ Can't save (marker not found)"); return
        Path(path).write_bytes(data)
        self.uic.textEdit.append(f"     💾 Save >> {self.start:X}x{self.end:X} >> {os.path.basename(path)}")


    # Export Folder - N26T9_25
    def export_folder(self):
        out, lw = QFileDialog.getExistingDirectory(None, "Select Folder"), self.uic.listWidget
        if not (out and lw.count()):
            self.uic.textEdit.append("     ❌ Can't Export"); return

        with open(self.image, "rb") as f:
            for i in range(lw.count()):
                start, end = (int(x, 16) for x in lw.item(i).toolTip().split("x"))
                f.seek(start)
                if data := self._repaired(f.read(end - start)): Path(out, f"IMG_{i+1}.JPG").write_bytes(data)

        self.uic.textEdit.append(f"     💾 Export >> {out}")

# ════════════════════════════════════════════════════════════════════════════════════════════════════
# ════════════════════════════════════════════════════════════════════════════════════════════════════
    # Open Folder - N26T9_25 - OK - check error
    def open_folder(self):
        folder, self.image = QFileDialog.getExistingDirectory(None, "Select Folder"), ""
        if folder:
            with open("temp_rp", "wb") as w:  # nối mọi file trong folder
                for n in os.listdir(folder):
                    if os.path.isfile(p := os.path.join(folder, n)):
                        with open(p, "rb") as r: shutil.copyfileobj(r, w)
            self.uic.textEdit.append(f'📂 Folder: {folder}')
            self.image = "temp_rp"
        else: self.uic.textEdit.append("     ❌ Can't open folder")

        # Reset list & label
        self.uic.listWidget.clear()
        self.uic.label.clear()

        self.main()

    # Open File - N26T9_25 - OK - check error
    def open_file(self):
        self.image = QFileDialog.getOpenFileName(None, "Select File", None ,filter='JPEG files (*.JPEG *.JPG);;RAW files (*.CR2 *.CR3 *.NEF *.ARW *.RAF);;All files (*)')[0]
        if self.image: self.uic.textEdit.append(f'~~~~~~~~~~~~~~~~~~\n⭕ {os.path.basename(self.image)}')
        else: self.uic.textEdit.append(f'''     ❌ Can't open file''')

        # Reset list & label
        self.uic.listWidget.clear()
        self.uic.label.clear()

        # View
        self.main()
        
# ══════════════════════════════════════════ 🛰️ TOOLs 🛰️ ════════════════════════════════════════════
# ════════════════════════════════════════════════════════════════════════════════════════════════════
    # Replace x25805 (ransomwawre) - N3T9_25
    def hex_x25805(self):
        self.image_hex = QFileDialog.getOpenFileName(None, "Select File", None ,filter='JPEG files (*.JPEG *.JPG);;All files (*)')[0]

        if self.image_hex and self.image:
            # Open file ref
            with open(self.image_hex, 'rb') as f:
                d4t4_r3f = f.read()
            st4rt_ind3x = d4t4_r3f.index(b'\xFF\xD8') # Find fist -> byte FF DA
            end_ind3x = d4t4_r3f.rfind(b'\xFF\xDA')

            # Save header
            with open('temp_rp', 'wb') as f:
                f.write(d4t4_r3f[st4rt_ind3x:end_ind3x + 12])

            # Add from byte 153605 -> and
            with open(self.image, 'rb') as f1, open('temp_rp', 'ab') as f2:
                f2.write(f1.read()[153605:None])

            # View & add text
            self.uic.textEdit.append(f'✂ Replace x25805 of file {os.path.basename(self.image)} with "SOS marker" of file {os.path.basename(self.image_hex)}')
            self.image = 'temp_rp'
            self.main()

    # File RAW
    def RAW(self):
        self.image_raw = QFileDialog.getOpenFileName(None, "Select File", None ,filter='RAW files (*.CR2 *.NEF *.ARW);;All files (*)')[0]

        if self.image_raw and self.image:

            image_extension = self.image_raw.split('.')[-1].lower()
            folder0 = f"{os.path.dirname(self.image)}/Repaired"
            file0 = f"{folder0}/{os.path.basename(self.image)}"

            if not os.path.exists(folder0):
                os.makedirs(folder0)

            if image_extension in ["cr2"]:
                # Lấy header
                with open(self.image_raw, 'rb') as f:
                    d4t4_r3f = f.read()
                end_ind3x = d4t4_r3f.find(binascii.unhexlify('FFD8FFC400'))
                if end_ind3x != -1:
                    with open("temp_rp.raw", 'wb') as f:
                        f.write(d4t4_r3f[:end_ind3x])

                #Add byte FFD8FFC4 -> cuối file
                with open(self.image, 'rb') as f:
                    d4t4_cr2 = f.read()
                    with open("temp_rp.raw", 'ab') as d4t4_cr2_2:
                        d4t4_cr2_2.write(d4t4_cr2[d4t4_cr2.index(bytes.fromhex('FFD8FFC400')):None])


            elif image_extension in ["arw", "nef"]:
                #-------------------------------------------------
                # Lấy header
                with open(self.image_raw, 'rb') as f:
                    data = f.read()
                    d4t4_4rw, index = self.RAW_NEF_ARW(data)

                with open("temp_rp.raw", 'wb') as f:
                    f.write(d4t4_4rw[:index])
                #-------------------------------------------------
                # Add byte 00000 -> cuối tệp
                with open(self.image, 'rb') as f:
                    data = f.read()
                    d4t4_4rw, index = self.RAW_NEF_ARW(data)

                with open("temp_rp.raw", 'ab') as f:
                    f.write(d4t4_4rw[index:])
                #-------------------------------------------------

            # Conver JPG
            command = [f"{os.getcwd()}/Irfan/i_view64.exe", "temp_rp.raw", "/convert=" + f"temp_img.JPG"]
            subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            os.replace("temp_rp.raw", file0)

            self.image = 'temp_img.JPG'
            self.main()

    # Get data
    def RAW_NEF_ARW(self, d4t4_4rw):
        index = d4t4_4rw.rfind(bytes.fromhex('FFD90000')) + 2
        while index < len(d4t4_4rw) and d4t4_4rw[index] == 0x00:
            index += 1

        return d4t4_4rw, index

    # Hex Dismen
    def none_Hex(self):
        self.image_hex = QFileDialog.getOpenFileName(None, "Select File", None ,filter='JPEG files (*.JPEG *.JPG);; All files (*)')[0]

        if self.image_hex and self.image:
            with open(self.image_hex, 'rb') as f:
                d4t4_r3f = f.read()
            st4rt_ind3x = d4t4_r3f.index(b'\xFF\xD8')
            end_ind3x = d4t4_r3f.rfind(b'\xFF\xDA')

            with open(self.image, 'rb') as r, open('temp_rp', 'wb') as w:
                w.write(d4t4_r3f[st4rt_ind3x:end_ind3x + 12] + r.read()[end_ind3x + 12:])

            self.image = 'temp_rp'
            self.main()



# ══════════════════════════════════════════ 🔓 About 🔓 ════════════════════════════════════════════
# ════════════════════════════════════════════════════════════════════════════════════════════════════
    # About - D10M05Y26
    def show_about(self):
        if not hasattr(self, "about"):
            self.about = QMainWindow()

            self.uic_about = Ui_About()
            self.uic_about.setupUi(self.about)

            self.uic_about.b_OK.clicked.connect(self.about.close)

        self.about.show()
        self.about.raise_()
        self.about.activateWindow()

# ════════════════════════════════════════ 💻 UI CREATE 💻 ══════════════════════════════════════════
# ════════════════════════════════════════════════════════════════════════════════════════════════════
    # Create New - N16T10_24
    def show_Create_New(self):
        self.Create_New = QMainWindow()
        self.uic_Create_New = Ui_Create_New()
        self.uic_Create_New.setupUi(self.Create_New)
        self.Create_New.show()

        # self.uic_Create_New.b_add.clicked.connect(self.add_create)
        # self.uic_Create_New.checkBox_2.stateChanged.connect(self.on_checkbox_changed)

        # OK & Exit
        self.uic_Create_New.b_OK.clicked.connect(self.Create_New_OK)
        self.uic_Create_New.b_Cancel.clicked.connect(lambda: self.Create_New.close())




    # OK (main) - N10T5_25
    def Create_New_OK(self):
        # Exit & delete file
        self.Create_New.close()
        selected_item = self.uic_Create_New.listWidget.currentItem()  # Lấy item được chọn


        if selected_item.text() == "Auto" and self.image:
            offset = 153605 if self.uic_Create_New.checkBox.isChecked() else 0
            # Chỉ đọc từ offset, không nạp cả file vào RAM rồi mới cắt
            with open(self.image, 'rb') as f1, open('temp_rp', 'wb') as f2:
                f1.seek(offset)
                shutil.copyfileobj(f1, f2)

            self.uic.textEdit.append('     🔍 Please wait...')

            proc = _run(["./tool/JpegRecovery.exe", "temp_rp"], wait=False)
            while proc.poll() is None:
                QApplication.processEvents(); time.sleep(0.01)

            if os.path.exists("temp_rp.jpg"):
                os.replace("temp_rp.jpg", "temp_rp")
                self.uic.textEdit.insertPlainText('     👉 Successful processing')
                self.image = "temp_rp"
                self.main()
            else:
                self.uic.textEdit.insertPlainText('     👉 Processing failed')

# ═════════════════════════════════════════ 💻 UI EDIT 💻 ═══════════════════════════════════════════
# ════════════════════════════════════════════════════════════════════════════════════════════════════
    # Edit Image - D10M05Y26
    def show_image_editor(self):
        self.sr_edit_image = QMainWindow()
        self.uic_edit_image = Ui_Edit_Image()
        self.uic_edit_image.setupUi(self.sr_edit_image)
        self.sr_edit_image.show()

        uic_ei = self.uic_edit_image
        cv = ImageCanvas()
        uic_ei.mainLayout.replaceWidget(uic_ei.label, cv)
        uic_ei.label.deleteLater(); uic_ei.label = cv

        # Chọn MCU <-> spinbox; zoom (wheel, Ctrl +/-/0) không đụng MCU đã chọn
        cv.selected.connect(lambda x, y: (uic_ei.sbox_mcu_x.setValue(x), uic_ei.sbox_mcu_y.setValue(y)))
        for sb in (uic_ei.sbox_mcu_x, uic_ei.sbox_mcu_y):
            sb.valueChanged.connect(lambda _: cv.set_sel(uic_ei.sbox_mcu_x.value(), uic_ei.sbox_mcu_y.value()))
        for k, f in (("Ctrl++", 1.25), ("Ctrl+=", 1.25), ("Ctrl+-", 0.8)):
            QShortcut(QKeySequence(k), self.sr_edit_image, activated=lambda f=f: cv.zoom(f))
        QShortcut(QKeySequence("Ctrl+0"), self.sr_edit_image, activated=cv.fit)

        # Value
        self.im4g3 = ""

        if self.image:
            self.im4g3 = self.image
            self._ei_load(self.image)

        # Rút gọn phần self đi
        uic_ei.b_Open.clicked.connect(self.EI_open)
        uic_ei.b_Save.clicked.connect(self.EI_save)
        uic_ei.b_View.clicked.connect(self.EI_view)

        # Change num in slider
        uic_ei.slider_cr.valueChanged.connect(lambda v: uic_ei.l_cr.setText(f"{v}"))
        uic_ei.slider_cb.valueChanged.connect(lambda v: uic_ei.l_cb.setText(f"{v}"))
        uic_ei.slider_y.valueChanged.connect(lambda v: uic_ei.l_y.setText(f"{v}"))





    # Save - D10M05Y26
    def EI_save(self):
        # Replace - Cho phép di chuyển khi các phân vùng
        save_file = QFileDialog.getSaveFileName(None, "Save File", "" ,filter='JPEG files (*.JPG);; All files (*)')[0]
        if save_file and os.path.exists("temp_img.JPG"): shutil.copy("temp_img.JPG", save_file)




    # Hiển thị JPEG bytes lên canvas (kèm lưới MCU)
    def _ei_show(self, raw):
        if pm := to_pixmap(raw): self.uic_edit_image.label.set_pixmap(pm, jpeg_mcu(raw))


    # Decode MCU log + hiển thị file
    def _ei_load(self, path):
        _run(['./tool/JpegDecomp.exe', '-decode', '-fin', path, '-fout', "log_mcu.txt"])
        self._ei_show(Path(path).read_bytes())


    # Open File - D10M05Y26
    def EI_open(self):
        self.im4g3 = QFileDialog.getOpenFileName(None, "Select File", filter='JPEG files (*.JPEG *.JPG);;All files (*)')[0]
        Path("temp_img.JPG").unlink(missing_ok=True)
        self.uic_edit_image.label.clear()
        if self.im4g3: self._ei_load(self.im4g3)


    # View - D10M05Y26
    def EI_view(self):
        if not self.im4g3: return
        ui, src = self.uic_edit_image, self.im4g3
        v = lambda w: str(w.value())

        if ui.b0x_d3l3t3_2.isChecked():  # xoá đoạn giữa 2 MCU trước khi repair
            tags = [f"({x},{y})" for x, y in
                    (map(int, t.text().split(',')) for t in (ui.le_mcu_xy_1, ui.le_mcu_xy_2))]
            with open("log_mcu.txt", encoding="utf-8") as f:
                delete_mcu(src, "temp_img_fixed.JPG", [l.strip() for l in f if any(t in l for t in tags)])
            src = "temp_img_fixed.JPG"

        mode = "delete" if ui.radio1.isChecked() else "insert"
        cd = [a for i, w in enumerate((ui.slider_y, ui.slider_cb, ui.slider_cr)) for a in ("cdelta", str(i), v(w))]
        _run(["./tool/JpegRepair.exe", src, "temp_img.JPG", "dest", v(ui.sbox_mcu_y), v(ui.sbox_mcu_x), mode, v(ui.spinBox), *cd])
        if os.path.exists("temp_img.JPG"): self._ei_show(Path("temp_img.JPG").read_bytes())




    def show(self):
        self.main_win.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("windowsvista")

    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
