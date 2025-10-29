"""1. Thay header lớn hơn kích thước ảnh -> xám ở đáy -> bé hơn
    2. Thay header bé hơn không -> xám ở đáy -> lớn hơn"""
import sys, os, subprocess, binascii, shutil

# Proce Image
from PIL import Image, ImageFile
from io import BytesIO

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon, QImage, QPainter, QFontMetrics
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidget, QListWidgetItem, QListView

from Run.read_data import read_data
from Run.view_mcu import MCUViewer

from GUI.Sreen.GUI import Ui_MainWindow
from GUI.Widget.About import Ui_About
from GUI.Widget.Create import Ui_Create_New
from GUI.Widget.Edit_Image import Ui_Edit_Image

class MainWindow:
    def __init__(self):
        self.main_win = QMainWindow()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self.main_win)

        ImageFile.LOAD_TRUNCATED_IMAGES = True

        # //////////////////////////////////////////
        # //////////////////////////////////////////
        self.uic.listWidget.setViewMode(QListView.ViewMode.IconMode)
        self.uic.listWidget.setFlow(QListView.Flow.LeftToRight)
        self.uic.listWidget.setWrapping(True)
        self.uic.listWidget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.uic.listWidget.setMovement(QListView.Movement.Static)
        self.uic.listWidget.setSpacing(12)

        # THAM SỐ: thay đổi nếu muốn thumbnail khác
        self.thumb_w = 89
        self.thumb_h = 89
        self.thumb_size = QSize(self.thumb_w, self.thumb_h)
        self.uic.listWidget.setIconSize(self.thumb_size)

        # Tính chiều cao cho text (dựa vào font hiện tại)
        fm = QFontMetrics(self.uic.listWidget.font())
        text_h = fm.height() + 4  # + padding nhỏ

        # Grid size = thumbnail + khoảng cho text + padding
        grid_w = self.thumb_w + 20
        grid_h = self.thumb_h + text_h + 18
        self.grid_size = QSize(grid_w, grid_h)
        self.uic.listWidget.setGridSize(self.grid_size)

        # //////////////////////////////////////////
        # //////////////////////////////////////////
        # self.uic.splitter.setStretchFactor(0 , 1) 
        self.uic.splitter.setSizes([400, 100])
        self.uic.splitter_2.setSizes([220, 100])

        # Open File, Folder - N10T10_2024
        self.uic.Open_File.triggered.connect(self.open_file)
        self.uic.Open_Folder.triggered.connect(self.open_folder)

        # Save File, Export Folder - N13T10_2024
        self.uic.Save.triggered.connect(self.save_file)
        self.uic.Export.triggered.connect(self.export_folder)

        self.uic.None_Hex.triggered.connect(self.none_Hex)
        self.uic.x25805.triggered.connect(self.hex_x25805)
        self.uic.RAW.triggered.connect(self.RAW)

        # Show Edit Image, About, Create New - N17T10_2024
        self.uic.Edit_Image.triggered.connect(self.show_Edit_Image)
        self.uic.About.triggered.connect(self.show_About)
        self.uic.Create_New.triggered.connect(self.show_Create_New)

        self.uic.listWidget.itemClicked.connect(self.item_clicked)

        # self.uic.Open_File.setStatusTip("Open a file from your computer")

        # Value - N13T10_2024
        self.image = ""
        self.start = self.end = 0


    def make_square_thumbnail(self, pixmap: QPixmap) -> QPixmap:
        """
        Vẽ pixmap đã scaled vào 1 QPixmap kích thước cố định (self.thumb_size),
        canh giữa, background trắng (hoặc trong suốt nếu bạn muốn).
        """
        # Scale giữ tỉ lệ
        scaled = pixmap.scaled(
            self.thumb_w, self.thumb_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        base = QPixmap(self.thumb_w, self.thumb_h)
        base.fill(Qt.GlobalColor.white)  # đổi sang transparent nếu muốn

        painter = QPainter(base)
        x = (self.thumb_w - scaled.width()) // 2
        y = (self.thumb_h - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        painter.end()
        
        return base

# ////////////////////////////////////////main\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def add_image(self, item_off):
        ioffset = item_off # .text() # Chuỗi kiểu "0xSTARTxEND" # Chuyển đổi hex -> offset
        self.start, self.end = map(lambda x: int(x, 16), ioffset.split('x'))

        with open(self.image, "rb") as file:
            file.seek(self.start) # Di chỏ đến offset
            data = file.read(self.end - self.start)
            # h34d3r = bytes.fromhex('FFD8FFE1007C45786966000049492A000800000003000E010200270000003200000012010300010000000100000031010200190000005A000000000000005265706169726564206279205175616E6720446169202020200000000000000000000009000000005265636F766572794A7065672000000000000000000000000000')

            pixmap = self.read_image(data)

            if pixmap:
                w = pixmap.width(); h = pixmap.height()

                thumb = self.make_square_thumbnail(pixmap)
                item = QListWidgetItem(QIcon(thumb), f"{w}x{h}") # item_off)

                # Ép size ô bằng grid_size để đồng nhất & căn chữ giữa
                item.setSizeHint(self.grid_size)
                item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)

                item.setToolTip(f"{item_off}")

                self.uic.listWidget.addItem(item)

    # Find marker - N24T1_25
    def main(self):
        if self.image: # Đọc file và thêm vào list
            list_offset = read_data(self.image)

            if list_offset != []:
                self.uic.textEdit.insertPlainText("..................Have")
                for offset in list_offset:
                    self.add_image(offset)
                    # self.uic.listWidget.addItem(offset)

            else: self.uic.textEdit.insertPlainText("..................Nothing")

# ////////////////////////////////////////Tool main\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Delete file - N3T9_25
    def delete(self, count = None):
        if count == 2:
            for file in ["blank.jpg", "header_out"]:
                if os.path.exists(file): os.remove(file)            

        else:
            for file in ["temp_rp", "temp_rp.raw"]:
                if os.path.exists(file): os.remove(file)


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


    def read_image(self, data):
        try:
            # Code beta
            raw_data = b"\xFF\xD8" + data
            img = Image.open(BytesIO(raw_data)).convert("RGB")
            w, h = img.size
            qimg = QImage(img.tobytes(), w, h, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)

            return pixmap

        except Exception as e:
            self.uic.textEdit.insertPlainText("...Faild")
            # print(traceback.format_exc())  # In chi tiết lỗi
            # Hoặc đơn giản: print(f"Lỗi: {e}")
            return None  # hoặc QPixmap() để trả về pixmap rỗng

    # Click Item & View - N24T1_25
    def item_clicked(self, item):
        ioffset = item.toolTip() # item.text() # Chuỗi kiểu "0xSTARTxEND" # Chuyển đổi hex -> offset
        self.start, self.end = map(lambda x: int(x, 16), ioffset.split('x'))

        with open(self.image, "rb") as file:
            file.seek(self.start) # Di chỏ đến offset
            data = file.read(self.end - self.start)

            pixmap = self.read_image(data)
            if pixmap:
                self.uic.label.setPixmap(QPixmap.fromImage(self.view_label(self.uic.label.width(), self.uic.label.height(), pixmap)))

                self.uic.label.setFixedSize(self.uic.label.width(), self.uic.label.height())
                self.uic.label.setScaledContents(False)


# ////////////////////////////////////////Tool\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# ////////////////////////////////////////----\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Save File - N26T9_25
    def save_file(self):
        self.save_image = QFileDialog.getSaveFileName(None, "Save File", None ,filter='JPEG files (*.JPG);; All files (*)')[0]
        if not (self.save_image and self.image and self.start):
            self.uic.textEdit.append("⚠️ Can't save")
            return
        
        header = bytes.fromhex('FFD8FFE1007C45786966000049492A000800000003000E010200270000003200000012010300010000000100000031010200190000005A000000000000005265706169726564206279205175616E6720446169202020200000000000000000000009000000005265636F766572794A7065672000000000000000000000000000')
        markers = {b"\xFF\xDB\x00\x84": "FFDB0084", b"\xFF\xDB\x00\x43": "FFDB0043"}

        with open(self.image, "rb") as file:
            file.seek(self.start) # Di chỏ đến offset
            cropped_data = file.read(self.end - self.start)

        fr0mh3x = next((v for k, v in markers.items() if k in cropped_data), None)

        if fr0mh3x:
            with open(self.save_image, 'wb') as f:
                f.write(header + cropped_data[cropped_data.index(bytes.fromhex(fr0mh3x)):])

            self.uic.textEdit.append(f'''💾 Save File: {self.start:X}x{self.end:X} --> {self.save_image}''')
        else:
            self.uic.textEdit.append("⚠️ Can't save (marker not found)")


    # Export Folder - N26T9_25
    def export_folder(self):
        self.export_folder = QFileDialog.getExistingDirectory(None, "Select Folder")
        if not (self.export_folder and self.uic.listWidget.count()):
            self.uic.textEdit.append("⚠️ Can't export folder")
            return

        header = bytes.fromhex('FFD8FFE1007C45786966000049492A000800000003000E010200270000003200000012010300010000000100000031010200190000005A000000000000005265706169726564206279205175616E6720446169202020200000000000000000000009000000005265636F766572794A7065672000000000000000000000000000')
        markers = {b"\xFF\xDB\x00\x84": "FFDB0084", b"\xFF\xDB\x00\x43": "FFDB0043"}

        with open(self.image, "rb") as f:
            for idx in range(self.uic.listWidget.count()):
                start, end = map(lambda x: int(x, 16), self.uic.listWidget.item(idx).text().split("x"))
                f.seek(start)
                cropped_data = f.read(end - start)

                fr0mh3x = next((v for k, v in markers.items() if k in cropped_data), None)
                if not fr0mh3x:
                    continue  # bỏ qua nếu không tìm thấy marker

                out_path = f"{self.export_folder}/OIMG_{idx+1}.JPG"
                with open(out_path, "wb") as out:
                    out.write(header + cropped_data[cropped_data.index(bytes.fromhex(fr0mh3x)):])

        self.uic.textEdit.append(f"💾 Export Folder: {self.export_folder}")


    # Open Folder - N26T9_25
    def open_folder(self):
        self.image = QFileDialog.getExistingDirectory(None, "Select Folder")
        # Reset list & label
        self.uic.listWidget.clear()
        self.uic.label.clear()

        if self.image != "":
            self.delete()
            # Read folder
            for i in os.listdir(self.image):
                if os.path.isfile(os.path.join(self.image, i)): # Check if it's a file (not a folder)
                    with open(f"{self.image}/{i}", "rb") as r:
                        with open("temp_rp", "ab") as w:
                            w.write(r.read())

            # View & log
            self.uic.textEdit.append(f'📂 Open Folder: {self.image}')
            self.image = "temp_rp"

        self.main()


    # Open File - N26T9_25
    def open_file(self):
        self.image = QFileDialog.getOpenFileName(None, "Select File", None ,filter='JPEG files (*.JPEG *.JPG);;RAW files (*.CR2 *.CR3 *.NEF *.ARW *.RAF);;All files (*)')[0]
        # Reset list & label
        self.uic.listWidget.clear()
        self.uic.label.clear()

        if self.image != "":
            self.uic.textEdit.append(f'📂 Open File: {self.image}')
        else:
            self.uic.textEdit.append(f'''⚠️ Can't open file''')
            
        # View
        self.main()
        
# ////////////////////////////////////////Tool\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Replace x25805 (ransomwawre) - N3T9_25
    def hex_x25805(self):
        self.image_hex = QFileDialog.getOpenFileName(None, "Select File", None ,filter='JPEG files (*.JPEG *.JPG);;All files (*)')[0]

        if self.image_hex != "" and self.image != "":
            self.delete()
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

        if self.image_raw != "":
            self.delete()

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

        if self.image_hex != "":
            self.delete()

            with open(self.image_hex, 'rb') as f:
                d4t4_r3f = f.read()
            st4rt_ind3x = d4t4_r3f.index(b'\xFF\xD8')
            end_ind3x = d4t4_r3f.rfind(b'\xFF\xDA')

            with open(self.image, 'rb') as r, open('temp_rp', 'wb') as w:
                w.write(d4t4_r3f[st4rt_ind3x:end_ind3x + 12] + r.read()[end_ind3x + 12:])

            self.image = 'temp_rp'
            self.main()

# ////////////////////////////////////////About\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # About - N16T10_24
    def show_About(self):
        self.about = QMainWindow()
        self.uic_about = Ui_About()
        self.uic_about.setupUi(self.about)
        self.about.show()

        # Exit
        self.uic_about.b_OK.clicked.connect(lambda: self.about.close())

# ////////////////////////////////////////Tool Create\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# ////////////////////////////////////////Tool Create\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

    # Create New - N16T10_24
    def show_Create_New(self):
        self.Create_New = QMainWindow()
        self.uic_Create_New = Ui_Create_New()
        self.uic_Create_New.setupUi(self.Create_New)
        self.Create_New.show()

        self.uic_Create_New.b_add.clicked.connect(self.add_create)

        # OK & Exit
        self.uic_Create_New.b_OK.clicked.connect(self.Create_New_OK)
        self.uic_Create_New.b_Cancel.clicked.connect(lambda: self.Create_New.close())


    def add_create(self):
        w, h = self.uic_Create_New.ledit_pixel_w.text(), self.uic_Create_New.ledit_pixel_h.text()

        byte000x = self.uic_Create_New.cbox_dqt.currentText()
        byte2x = self.uic_Create_New.cbox_fac.currentText()

        item = f"{byte000x} - {w} x {h} - {byte2x}"

        # Nếu có rồi bỏ qua
        if self.uic_Create_New.listWidget.findItems(item, Qt.MatchFlag.MatchExactly): pass
        else: self.uic_Create_New.listWidget.addItem(item)

    # OK (main) - N10T5_25
    def Create_New_OK(self):
        # Exit & delete file
        self.delete()
        self.Create_New.close()
        
        selected_item = self.uic_Create_New.listWidget.currentItem()  # Lấy item được chọn
        if selected_item.text() != "Auto":
            # text = selected_item.text()  # Lấy văn bản của item
            # print(f"Item được chọn: {text}")
            # Tách chuỗi dựa trên dấu " - " và " x "
            text = selected_item.text()
            text = text.split("|")[0].strip()
            parts = text.replace(" x ", " - ").split(" - ")

            # Gán giá trị cho các biến
            byte000x = parts[0].strip()  # "0001" or 0002
            w, h = parts[1].strip(), parts[2].strip() # 6000x4000
            byte2x = parts[3].strip()    # 21 or 22, 11, 41


            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # RUN
            pr0c = subprocess.Popen(["./Tool/create_header.exe", byte000x, w, h, byte2x], startupinfo=startupinfo)
            while pr0c.poll() is None:
                QtWidgets.QApplication.processEvents()
            pr0c.wait()


            with open(f'header_out', 'rb') as r:
                data_header = r.read()

            if self.uic_Create_New.checkBox.isChecked() == True:
                # Read file & Write from x25805
                with open(self.image, 'rb') as f1, open('temp_rp', 'wb') as f2:
                    f2.write(data_header + f1.read()[153605:None])

            else:
                with open(self.image, 'rb') as f1, open('temp_rp', 'wb') as f2:
                    f2.write(data_header + f1.read())

            self.delete(2)
            self.image = "temp_rp"
            # print("Chay file main")
            self.main()



        # Using JpegRecovery
        else:
            # Read file & Write from x25805
            if self.uic_Create_New.checkBox.isChecked() == True:
                with open(self.image, 'rb') as f1, open('temp_rp', 'wb') as f2:
                    f2.write(f1.read()[153605:None])
            else:
                with open(self.image, 'rb') as f1, open('temp_rp', 'wb') as f2:
                    f2.write(f1.read())                

            self.uic.textEdit.append(f'🔍 Please wait for image processing')

            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # RUN
            pr0c = subprocess.Popen(["./Tool/JpegRecovery.exe","temp_rp"], startupinfo=startupinfo)
            while pr0c.poll() is None:
                QtWidgets.QApplication.processEvents()
            pr0c.wait()

            if os.path.exists("temp_rp.jpg"):
                # Rename & delete
                self.delete()
                os.rename("temp_rp.jpg", "temp_rp")

                self.uic.textEdit.insertPlainText(f'👉 Successful processing')
                self.image = "temp_rp"
                self.main()
            else:
                self.uic.textEdit.insertPlainText(f'👉 Processing failed')

# ////////////////////////////////////////Tool Edit\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# ////////////////////////////////////////Tool Edit\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Edit Image - N26T10_25
    def show_Edit_Image(self):
        self.sr_edit_image = QMainWindow()
        self.uic_edit_image = Ui_Edit_Image()
        self.uic_edit_image.setupUi(self.sr_edit_image)
        self.sr_edit_image.show()

        # Value
        self.im4g3 = self.ins3rt_d3l3t3 = ""

        if self.image:
            self.im4g3 = self.image

            pix = QPixmap(self.image)
            self.uic_edit_image.label.setPixmap(QPixmap.fromImage(self.view_label(self.uic_edit_image.label.width(), self.uic_edit_image.label.height(), pix)))
            self.uic_edit_image.sbox_pixel_h.setValue(pix.height())
            self.uic_edit_image.sbox_pixel_w.setValue(pix.width())

        self.uic_edit_image.b_Open.clicked.connect(self.EI_Open)
        self.uic_edit_image.b_Save.clicked.connect(self.EI_Save)
        self.uic_edit_image.b_View.clicked.connect(self.EI_View)

        self.uic_edit_image.b_pos.clicked.connect(lambda: self.EI_view_mcu())

        self.uic_edit_image.b0x_d3l3t3.clicked.connect(self.EI_checkbox)
        self.uic_edit_image.b0x_ins3rt.clicked.connect(self.EI_checkbox)

        # Change num in slider
        self.uic_edit_image.slider_cr.valueChanged.connect(lambda link: self.uic_edit_image.l_cr.setText(f"Cr = {self.uic_edit_image.slider_cr.value()}"))
        self.uic_edit_image.slider_cb.valueChanged.connect(lambda link: self.uic_edit_image.l_cb.setText(f"Cb = {self.uic_edit_image.slider_cb.value()}"))
        self.uic_edit_image.slider_y.valueChanged.connect(lambda link: self.uic_edit_image.l_y.setText(f"Y = {self.uic_edit_image.slider_y.value()}"))

    # Save - N26T9_25
    def EI_Save(self):
        # Replace - Cho phép di chuyển khi các phân vùng
        save_file = QFileDialog.getSaveFileName(None, "Save File", "" ,filter='JPEG files (*.JPG);; All files (*)')[0]
        if save_file and os.path.exists("temp_img.JPG"): shutil.copy("temp_img.JPG", save_file)

    # Check box - N26T9_25
    def EI_checkbox(self):
        if self.uic_edit_image.b0x_ins3rt.isChecked():
            self.ins3rt_d3l3t3 = "insert"
            self.uic_edit_image.b0x_d3l3t3.setChecked(False)
        else:
            self.ins3rt_d3l3t3 = "delete"
            self.uic_edit_image.b0x_ins3rt.setChecked(False)

    # Open File - N26T9_25
    def EI_Open(self):
        self.im4g3 = QFileDialog.getOpenFileName(None, "Select File" , filter='JPEG files (*.JPEG *.JPG);;All files (*)')[0]
        # Delete File & clear
        if os.path.exists("temp_img.JPG"): os.remove("temp_img.JPG")
        self.uic_edit_image.label.clear()

        
        # View
        if self.im4g3:
            with open(self.im4g3, "rb") as f:
                raw_data = f.read()

            pixmap = self.read_image(raw_data[2:])

            if pixmap:
                self.uic_edit_image.label.setPixmap(QPixmap.fromImage(self.view_label(self.uic_edit_image.label.width(), self.uic_edit_image.label.height(), pixmap)))

                w = pixmap.width(); h = pixmap.height()
                self.uic_edit_image.sbox_pixel_h.setValue(h)
                self.uic_edit_image.sbox_pixel_w.setValue(w)

    def EI_view_mcu(self):
        self.mcu_viewer = MCUViewer()
        self.mcu_viewer.show()
        
    # View - N26T10_25
    def EI_View(self):
        # Quy đổi giá trị & gán vào biến
        # Ex:       mcu_x = str(self.uic_edit_image.sbox_mcu_x.value())
        ui = self.uic_edit_image # Code rút gọn
        cr, cb, y = map(lambda s: str(s.value()), [ui.slider_cr, ui.slider_cb, ui.slider_y])
        blocks, mcu_x, mcu_y = map(lambda s: str(s.value()), [ui.spinBox, ui.sbox_mcu_x, ui.sbox_mcu_y])

        # pixel_h = str(self.uic_edit_image.sbox_pixel_h.value())
        # pixel_w = str(self.uic_edit_image.sbox_pixel_w.value())

        fil30 = "temp_img.JPG"
        # Run JpegRepair
        if self.im4g3:
            #                                                     file in        file out
            if self.ins3rt_d3l3t3: pr0c = ["./Tool/JpegRepair.exe", self.im4g3, "temp_img.JPG", "dest", mcu_y, mcu_x, self.ins3rt_d3l3t3, blocks, "cdelta",str(0), y, "cdelta",str(1), cb, "cdelta",str(2), cr]
            else: pr0c = ["./Tool/JpegRepair.exe", self.im4g3, "temp_img.JPG", "cdelta",str(0), y, "cdelta",str(1), cb, "cdelta",str(2), cr]

            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(pr0c, startupinfo=startupinfo)   
            # View
            self.uic_edit_image.label.setPixmap(QPixmap.fromImage(self.view_label(self.uic_edit_image.label.width(), self.uic_edit_image.label.height(), QPixmap(fil30))))



    def show(self):
        self.main_win.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
