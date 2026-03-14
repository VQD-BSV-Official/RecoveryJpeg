import sys, struct
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QScrollArea, 
                             QVBoxLayout, QWidget, QFileDialog, QMessageBox)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QWheelEvent
from PyQt6.QtCore import Qt, QPoint, QRect

class MCUViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()


        self.scale_factor = 1.0
        self.selected_mcu = None
        self.image_path = None
        
    def initUI(self):
        self.setWindowTitle('MCU Viewer - WxH')
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # Create image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.on_image_click
        
        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)
        
        # Create menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        
        open_action = file_menu.addAction('Open Image')
        open_action.triggered.connect(self.open_image)
        
        # Status bar
        self.statusBar().showMessage('Ready')
        



    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open Image', '', 'Image Files (*.jpg *.jpeg *.png *.bmp)'
        )
        
        if file_path:
            self.image_path = file_path
            self.mcu_width, self.mcu_height = self.get_size_mcu(self.image_path)
            self.setWindowTitle(f'MCU Viewer - {self.mcu_width}x{self.mcu_height}')
            self.load_image()
            



    def load_image(self):
        try:
            # Load image
            self.original_pixmap = QPixmap(self.image_path)
            if self.original_pixmap.isNull():
                raise ValueError("Could not load image")
                
            self.display_image()
            self.statusBar().showMessage(f'Image loaded: {self.image_path}')
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load image: {str(e)}')
            


    def display_image(self):
        if hasattr(self, 'original_pixmap'):
            # Scale the image
            scaled_pixmap = self.original_pixmap.scaled(
                int(self.original_pixmap.width() * self.scale_factor),
                int(self.original_pixmap.height() * self.scale_factor),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Draw MCU grid and selection
            painter = QPainter(scaled_pixmap)
            self.draw_mcu_grid(painter, scaled_pixmap.size())
            
            if self.selected_mcu:
                self.draw_selected_mcu(painter, self.selected_mcu, scaled_pixmap.size())
            
            painter.end()
            
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.resize(scaled_pixmap.size())
            


    def draw_mcu_grid(self, painter, image_size):
        pen = QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DotLine)
        painter.setPen(pen)
        
        # Draw vertical lines for MCU width
        for x in range(0, image_size.width(), int(self.mcu_width * self.scale_factor)):
            painter.drawLine(x, 0, x, image_size.height())
        
        # Draw horizontal lines for MCU height
        for y in range(0, image_size.height(), int(self.mcu_height * self.scale_factor)):
            painter.drawLine(0, y, image_size.width(), y)
            


    def draw_selected_mcu(self, painter, mcu_coords, image_size):
        pen = QPen(Qt.GlobalColor.red, 3)
        painter.setPen(pen)
        
        x, y = mcu_coords
        rect = QRect(
            int(x * self.mcu_width * self.scale_factor),
            int(y * self.mcu_height * self.scale_factor),
            int(self.mcu_width * self.scale_factor),
            int(self.mcu_height * self.scale_factor)
        )
        
        painter.drawRect(rect)
        


    def on_image_click(self, event):
        if not hasattr(self, 'original_pixmap'):
            return
            
        if event.button() == Qt.MouseButton.LeftButton:
            # Get click position relative to image
            pos = event.pos()
            
            # Calculate MCU coordinates
            mcu_x = int(pos.x() / (self.mcu_width * self.scale_factor))
            mcu_y = int(pos.y() / (self.mcu_height * self.scale_factor))
            
            # Get image dimensions in MCUs
            img_width_mcu = int(self.original_pixmap.width() / self.mcu_width)
            img_height_mcu = int(self.original_pixmap.height() / self.mcu_height)
            
            # Check if click is within image bounds
            if 0 <= mcu_x < img_width_mcu and 0 <= mcu_y < img_height_mcu:
                self.selected_mcu = (mcu_x, mcu_y)
                self.display_image()
                
                # Show MCU info in status bar
                self.statusBar().showMessage(
                    f'MCU selected: ({mcu_x}, {mcu_y}) - '
                    f'Pixel position: ({mcu_x * self.mcu_width}, {mcu_y * self.mcu_height})'
                )
                
                # Zoom to selected MCU
                self.zoom_to_mcu(mcu_x, mcu_y)
                


    def zoom_to_mcu(self, mcu_x, mcu_y):
        # Calculate the position of the MCU in the scaled image
        mcu_pixel_x = int(mcu_x * self.mcu_width * self.scale_factor)
        mcu_pixel_y = int(mcu_y * self.mcu_height * self.scale_factor)
        
        # Center the scroll area on the MCU
        self.scroll_area.ensureVisible(
            mcu_pixel_x + self.mcu_width // 2,
            mcu_pixel_y + self.mcu_height // 2,
            self.mcu_width,
            self.mcu_height
        )
        


    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom with Ctrl + Mouse Wheel
            zoom_in = event.angleDelta().y() > 0
            
            if zoom_in:
                self.scale_factor *= 1.2
            else:
                self.scale_factor /= 1.2
                
            # Limit zoom range
            self.scale_factor = max(0.1, min(self.scale_factor, 10.0))
            
            self.display_image()
            
            # Keep the selected MCU visible after zoom
            if self.selected_mcu:
                self.zoom_to_mcu(*self.selected_mcu)
                
            event.accept()
        else:
            super().wheelEvent(event)
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            self.scale_factor *= 1.2
            self.display_image()
        elif event.key() == Qt.Key.Key_Minus:
            self.scale_factor /= 1.2
            self.display_image()
        elif event.key() == Qt.Key.Key_R:
            self.scale_factor = 1.0
            self.selected_mcu = None
            self.display_image()
        else:
            super().keyPressEvent(event)







    def get_size_mcu(self, jpeg_path):
        """
        Xác định kích thước MCU (Minimum Coded Unit) của tệp JPEG.
        Trả về tuple (width, height) của MCU tính bằng pixel.
        """
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
    

# def main():
#     app = QApplication(sys.argv)
#     viewer = MCUViewer()
#     viewer.show()
#     sys.exit(app.exec())

# if __name__ == '__main__':
#     main()