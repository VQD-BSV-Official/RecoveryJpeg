import sys, os, subprocess, binascii

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon, QImage, QPainter
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog

from GUI.GUI import Ui_MainWindow
from GUI.About import Ui_About
from GUI.Create import Ui_Create_New
from GUI.Edit_Image import Ui_Edit_Image

class MainWindow:
    def __init__(self):
        self.main_win = QMainWindow()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self.main_win)

        # Label copyright - N10T10_2024
        # self.uic.label_Copyright.setText('Author & Developed by: <a href="https://www.facebook.com/QuangDaiVQD">Vũ Quang Đại</a>')
        # self.uic.label_Copyright.setOpenExternalLinks(True)
        # self.uic.label_Copyright.linkActivated.connect(lambda link: QDesktopServices.openUrl(QUrl(link)))

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

        self.status("Ready")
        # self.uic.Open_File.setStatusTip("Open a file from your computer")

        # Value - N13T10_2024
        self.image = ""
        self.start = self.end = 0



# ////////////////////////////////////////main\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Find marker - N11T1_2025
    def main(self):
        if self.image != "":
            # Read 
            with open(self.image, 'rb') as dump:

                while True:
                    pos = dump.tell()
                    buf = dump.read(512)
                    if not buf:
                        break

                    idx = buf.find(b'\xFF\xDB\x00\x84')
                    if idx < 0:
                        idx = buf.find(b'\xFF\xDB\x00\x43')
                        if idx < 0:
                            dump.seek(pos + 512)
                            continue

                    dump.seek(offset_start := pos + idx)

                    while True:
                        pos_end = dump.tell()
                        buf_end = dump.read(512)
                        if not buf_end:
                            break

                        idx_end = buf_end.find(b'\xFF\xD9')
                        if idx_end > 0:
                            offset_end = pos_end + idx_end + 2


                            print(f'>> {offset_start:X}x{offset_end:X}')
                            self.uic.listWidget.addItem(f'{offset_start:X}x{offset_end:X}')

                            dump.seek(offset_end)
                            break

                        else:
                            continue


        # OLD VERSION
            # with open(self.image, "rb") as file:
            #     data = file.read()

            #     # Danh sách các loại marker
            #     markers = [b"\xFF\xDB\x00\x84", b"\xFF\xDB\x00\x43"]
            #     end_marker = b"\xFF\xD9"

            #     for marker in markers:
            #         start_offset = data.find(marker)

            #         while start_offset != -1:
            #             end_offset = data.find(end_marker, start_offset)
            #             if end_offset != -1:

            #                 # ADD List
            #                 self.uic.listWidget.addItem(f"{str(start_offset)}x{str(end_offset)}")
            #                 start_offset = data.find(marker, end_offset)
            #             else:
            #                 break

# ////////////////////////////////////////Tool main\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Status - N12T1_25
    def status(self, mes):
        self.uic.statusBar.showMessage(mes)

    # Delete file - N6T10_2024
    def delete(self):
        if os.path.exists("BSVRecovery.vn"):
            os.remove("BSVRecovery.vn")

        elif os.path.exists("BSVRecovery.vn.raw"):
            os.remove("BSVRecovery.vn.raw")

    # View image (label) - N12T1_25
    def view_label(self, label_width, label_height, pixmap):
        # Tạo QImage với kích thước của QLabel
        image = QImage(label_width, label_height, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)  # Nền trong suốt

        # Tính toán kích thước ảnh giữ tỷ lệ
        scaled_pixmap = pixmap.scaled(
            label_width,
            label_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Dùng QPainter để căn giữa ảnh trên QLabel
        painter = QPainter(image)
        x_offset = (label_width - scaled_pixmap.width()) // 2
        y_offset = (label_height - scaled_pixmap.height()) // 2
        painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
        painter.end()

        return image        

    # Click Item & View - N11T1_2025
    def item_clicked(self, item):
        ioffset = item.text() # Chuyển đổi hex -> offset
        self.start, self.end = map(lambda x: int(x, 16), ioffset.split('x'))

        with open(self.image, "rb") as file:
            data = file.read()
            h34d3r = bytes.fromhex('FFD8FFE1007C45786966000049492A000800000003000E010200270000003200000012010300010000000100000031010200190000005A00000000000000526570616972656420627920425356205265636F76657279200000000000000000000009000000005265636F766572794A7065672000000000000000000000000000')
            
            pixmap = QPixmap() # Load byte (image)
            if pixmap.loadFromData(h34d3r + data[self.start:self.end + 2]):

                image = self.view_label(self.uic.label.width(), self.uic.label.height(), pixmap)
                self.uic.label.setPixmap(QPixmap.fromImage(image))

            else:
                print("Không thể tải dữ liệu hình ảnh!")

    # Save File - N7T10_2024
    def save_file(self):
        self.save_image = QFileDialog.getSaveFileName(None, "Save File", None ,filter='JPEG files (*.JPG);; All files (*)')[0]
        
        if self.save_image and self.image != '' and self.start != 0:
            with open(self.image, "rb") as file:
                data = file.read()
                cropped_data = data[self.start:self.end + 2]

            if b"\xFF\xDB\x00\x84" in cropped_data:
                fr0mh3x = 'FFDB0084'

            elif b"\xFF\xDB\x00\x43" in cropped_data:
                fr0mh3x = 'FFDB0043'

            h34d3r = bytes.fromhex('FFD8FFE1007C45786966000049492A000800000003000E010200270000003200000012010300010000000100000031010200190000005A00000000000000526570616972656420627920425356205265636F76657279200000000000000000000009000000005265636F766572794A7065672000000000000000000000000000')
            with open(self.save_image, 'wb') as f:
                f.write(h34d3r + cropped_data[cropped_data.index(bytes.fromhex(fr0mh3x)):])

            self.uic.textEdit.append(f'''💾 Save File: {self.save_image}''')
        else:
            self.uic.textEdit.append(f'''⚠️ Can't save''')
            
        # self.delete()

    # Open Folder - N13T10_2024
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
                        with open("BSVRecovery.vn", "ab") as w:
                            w.write(r.read())

            # View & log
            self.uic.textEdit.append(f'📂 Open Folder: {self.image}')
            self.image = "BSVRecovery.vn"
        self.main()

    # Open File - N10T10_2024
    def open_file(self):
        self.image = QFileDialog.getOpenFileName(None, "Select File", None ,filter='JPEG files (*.JPEG *.JPG);;RAW files (*.CR2 *.NEF *.ARW);;All files (*)')[0]
        # Reset list & label
        self.uic.listWidget.clear()
        self.uic.label.clear()

        if self.image != "":
            # Set name file & log
            self.status(os.path.basename(self.image))
            self.uic.textEdit.append(f'📂 Open File: {self.image}')
        else:
            self.uic.textEdit.append(f'''⚠️ Can't open file''')
            
        # View
        self.main()

    # Export Folder - N16T10_2024
    def export_folder(self):
        self.export_folder = QFileDialog.getExistingDirectory(None, "Select Folder")


        if self.uic.listWidget.count() != 0 and self.export_folder != '':
            self.export_count = 0
            for index in range(self.uic.listWidget.count()):
                item = self.uic.listWidget.item(index)

                ioffset = item.text()
                self.start, self.end = map(int, ioffset.split('x'))

                with open(self.image, "rb") as file:
                    data = file.read()
                    cropped_data = data[self.start:self.end + 2]

                if b"\xFF\xDB\x00\x84" in cropped_data:
                    fr0mh3x = 'FFDB0084'

                elif b"\xFF\xDB\x00\x43" in cropped_data:
                    fr0mh3x = 'FFDB0043'

                h34d3r = bytes.fromhex('FFD8FFE1007C45786966000049492A000800000003000E010200270000003200000012010300010000000100000031010200190000005A00000000000000526570616972656420627920425356205265636F76657279200000000000000000000009000000005265636F766572794A7065672000000000000000000000000000')
                self.export_count += 1
                with open(f"{self.export_folder}/IMG_{self.export_count}.JPG", 'wb') as f:
                    f.write(h34d3r + cropped_data[cropped_data.index(bytes.fromhex(fr0mh3x)):])

                self.uic.textEdit.append(f'💾 Export Folder: {self.export_folder}')
        else:
            self.uic.textEdit.append(f'''⚠️ Can't export folder''')

# ////////////////////////////////////////Tool\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Replace x25805 (ransomwawre) - N16T10_2024
    def hex_x25805(self):
        self.image_hex = QFileDialog.getOpenFileName(None, "Select File", None ,filter='JPEG files (*.JPEG *.JPG);;All files (*)')[0]

        if self.image_hex != "":
            self.delete()
            # Open file ref
            with open(self.image_hex, 'rb') as f:
                d4t4_r3f = f.read()
            st4rt_ind3x = d4t4_r3f.index(b'\xFF\xD8') # Find fist -> byte FF DA
            end_ind3x = d4t4_r3f.rfind(b'\xFF\xDA')

            # Save header
            with open('BSVRecovery.vn', 'wb') as f:
                f.write(d4t4_r3f[st4rt_ind3x:end_ind3x+12])

            # Add from byte 153605 -> and
            with open(self.image, 'rb') as f1, open('BSVRecovery.vn', 'ab') as f2:
                f2.write(f1.read()[153605:None])

            # View & add text
            self.uic.textEdit.append(f'✂ Replace x25805 of file {os.path.basename(self.image)} with "SOS marker" of file {os.path.basename(self.image_hex)}')
            self.image = 'BSVRecovery.vn'
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
                    with open("BSVRecovery.vn.raw", 'wb') as f:
                        f.write(d4t4_r3f[:end_ind3x])

                #Add byte FFD8FFC4 -> cuối file
                with open(self.image, 'rb') as f:
                    d4t4_cr2 = f.read()
                    with open("BSVRecovery.vn.raw", 'ab') as d4t4_cr2_2:
                        d4t4_cr2_2.write(d4t4_cr2[d4t4_cr2.index(bytes.fromhex('FFD8FFC400')):None])


            elif image_extension in ["arw", "nef"]:
                #-------------------------------------------------
                # Lấy header
                with open(self.image_raw, 'rb') as f:
                    data = f.read()
                    d4t4_4rw, index = self.RAW_NEF_ARW(data)

                with open("BSVRecovery.vn.raw", 'wb') as f:
                    f.write(d4t4_4rw[:index])
                #-------------------------------------------------
                # Add byte 00000 -> cuối tệp
                with open(self.image, 'rb') as f:
                    data = f.read()
                    d4t4_4rw, index = self.RAW_NEF_ARW(data)

                with open("BSVRecovery.vn.raw", 'ab') as f:
                    f.write(d4t4_4rw[index:])
                #-------------------------------------------------

            # Conver JPG
            command = [f"{os.getcwd()}/Irfan/i_view64.exe", "BSVRecovery.vn.raw", "/convert=" + f"IMG_.JPG"]
            subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            os.replace("BSVRecovery.vn.raw", file0)

            self.image = 'IMG_.JPG'
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

            with open(self.image, 'rb') as r, open('BSVRecovery.vn', 'wb') as w:
                w.write(d4t4_r3f[st4rt_ind3x:end_ind3x + 12] + r.read()[end_ind3x + 12:])

            self.image = 'BSVRecovery.vn'
            self.main()

# ////////////////////////////////////////Tool Edit\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # About - N16T10_2024
    def show_About(self):
        self.about = QMainWindow()
        self.uic_about = Ui_About()
        self.uic_about.setupUi(self.about)
        self.about.show()

        # Exit
        self.uic_about.b_OK.clicked.connect(lambda: self.about.close())

    # Create New - N16T10_2024
    def show_Create_New(self):
        self.Create_New = QMainWindow()
        self.uic_Create_New = Ui_Create_New()
        self.uic_Create_New.setupUi(self.Create_New)
        self.Create_New.show()

        # OK & Exit
        self.uic_Create_New.b_OK.clicked.connect(self.Create_New_OK)
        self.uic_Create_New.b_Cancel.clicked.connect(lambda: self.Create_New.close())

    # OK (main) - N17T10_2024
    def Create_New_OK(self):
        # Exit & delete file
        self.delete()
        self.Create_New.close()
        
        # Using JpegRecovery
        if self.uic_Create_New.checkBox.isChecked() == True:
            # Read file & Write from x25805
            with open(self.image, 'rb') as f1, open('BSVRecovery.vn', 'wb') as f2:
                f2.write(f1.read()[153605:None])

            self.uic.textEdit.append(f'🔍 Please wait for image processing')

            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # RUN
            pr0c = subprocess.Popen(["./Tool/JpegRecovery.exe","BSVRecovery.vn"], startupinfo=startupinfo)
            while pr0c.poll() is None:
                QtWidgets.QApplication.processEvents()
            pr0c.wait()

            if os.path.exists("BSVRecovery.vn.jpg"):
                # Rename & delete
                self.delete()
                os.rename("BSVRecovery.vn.jpg", "BSVRecovery.vn")

                self.uic.textEdit.append(f'👉 Processed')
                self.image = "BSVRecovery.vn"
                self.main()
            else:
                self.uic.textEdit.append(f'👉 Processed Fail')

    # Edit Image - N17T10_2024
    def show_Edit_Image(self):
        self.Sr33n_3dit_Im4g3 = QMainWindow()
        self.uic_3dit_Im4g3 = Ui_Edit_Image()
        self.uic_3dit_Im4g3.setupUi(self.Sr33n_3dit_Im4g3)
        self.Sr33n_3dit_Im4g3.show()

        # Value
        self.im4g3 = self.ins3rt_d3l3t3 = ""

        if self.image != '':
            self.uic_3dit_Im4g3.label.setPixmap(QPixmap(self.image))
            self.im4g3 = self.image

        self.uic_3dit_Im4g3.b_Open.clicked.connect(self.Edit_Image_Open)
        self.uic_3dit_Im4g3.b_Save.clicked.connect(self.Edit_Image_Save)
        self.uic_3dit_Im4g3.b_View.clicked.connect(self.Edit_Image_View)

        self.uic_3dit_Im4g3.b0x_d3l3t3.clicked.connect(self.checkbox)
        self.uic_3dit_Im4g3.b0x_ins3rt.clicked.connect(self.checkbox)

        # Change num in slider
        self.uic_3dit_Im4g3.slider_cr.valueChanged.connect(lambda link: self.uic_3dit_Im4g3.l_cr.setText(str(self.uic_3dit_Im4g3.slider_cr.value())))
        self.uic_3dit_Im4g3.slider_cb.valueChanged.connect(lambda link: self.uic_3dit_Im4g3.l_cb.setText(str(self.uic_3dit_Im4g3.slider_cb.value())))
        self.uic_3dit_Im4g3.slider_y.valueChanged.connect(lambda link: self.uic_3dit_Im4g3.l_y.setText(str(self.uic_3dit_Im4g3.slider_y.value())))

    # Save - N17T10_2024
    def Edit_Image_Save(self):
        save_file = QFileDialog.getSaveFileName(None, "Save File", None ,filter='JPEG files (*.JPG);; All files (*)')[0]
        # Replace
        if save_file and os.path.exists("IMG_.JPG"):
            os.replace("IMG_.JPG", save_file)

    # Check box - N17T10_2024
    def checkbox(self):
        if self.uic_3dit_Im4g3.b0x_ins3rt.isChecked():
            self.ins3rt_d3l3t3 = "insert"
            self.uic_3dit_Im4g3.b0x_d3l3t3.setChecked(False)

        elif self.uic_3dit_Im4g3.b0x_d3l3t3.isChecked():
            self.ins3rt_d3l3t3 = "delete"
            self.uic_3dit_Im4g3.b0x_ins3rt.setChecked(False)

    # Open File - N17T10_2024
    def Edit_Image_Open(self):
        self.im4g3 = QFileDialog.getOpenFileName(None, "Select File" ,filter='JPEG files (*.JPEG *.JPG);;All files (*)')[0]
        # Delete File & clear
        if os.path.exists("IMG_.JPG"):
            os.remove("IMG_.JPG")
        self.uic_3dit_Im4g3.label.clear()

        # View
        if self.im4g3 != "":
            self.uic_3dit_Im4g3.label.setPixmap(QPixmap(self.im4g3))

    # main - N17T10_2024
    def Edit_Image_View(self):
        # Quy đổi giá trị & gán vào biến
        cr = self.uic_3dit_Im4g3.slider_cr.value() # màu đỏ    cdelta 2
        cb = self.uic_3dit_Im4g3.slider_cb.value() # màu xanh  cdelta 1
        y = self.uic_3dit_Im4g3.slider_y.value() # ánh sáng    cdelta 0
        blocks = self.uic_3dit_Im4g3.spinBox.value()

        fil30 = "IMG_.JPG"

        # Run JpegRepair
        if self.im4g3 != "":
            if self.ins3rt_d3l3t3 != "":
                pr0c = ["./Tool/JpegRepair.exe", self.im4g3, fil30, "dest",str(0),str(0),str(self.ins3rt_d3l3t3),str(blocks), "cdelta",str(0),str(y), "cdelta",str(1),str(cb), "cdelta",str(2),str(cr)]

            else:
                pr0c = ["./Tool/JpegRepair.exe", self.im4g3, fil30,"cdelta",str(0),str(y), "cdelta",str(1),str(cb), "cdelta",str(2),str(cr)]
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(pr0c, startupinfo=startupinfo)   
            # RUN & View
            self.uic_3dit_Im4g3.label.setPixmap(QPixmap(fil30))

    def show(self):
        self.main_win.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
