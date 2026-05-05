import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QListWidget, 
                             QProgressBar, QFileDialog, QListWidgetItem, QFrame)
from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import QIcon, QFont, QPalette, QColor
from protocol import CrossLinkProtocol

class DeviceItem(QWidget):
    def __init__(self, name, ip, parent=None):
        super().__init__(parent)
        self.ip = ip
        layout = QHBoxLayout(self)
        
        self.name_label = QLabel(f"<b>{name}</b><br><small style='color: #666;'>{ip}</small>")
        layout.addWidget(self.name_label)
        
        self.send_btn = QPushButton("Send File")
        self.send_btn.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; padding: 5px 10px;")
        layout.addWidget(self.send_btn)

class CrossLinkGUI(QMainWindow):
    progress_signal = Signal(str, int, int)
    device_signal = Signal(dict)
    file_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.protocol = CrossLinkProtocol()
        self.protocol.on_device_discovered = self.device_signal.emit
        self.protocol.on_transfer_progress = self.progress_signal.emit
        self.protocol.on_file_received = self.file_signal.emit
        
        self.init_ui()
        self.setup_signals()
        
        self.protocol.start_discovery()
        self.protocol.start_server()

    def init_ui(self):
        self.setWindowTitle("CrossLink Standalone")
        self.setMinimumSize(400, 600)
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f7f9; }
            QFrame#MainFrame { background-color: white; border-radius: 20px; border: 1px solid #ddd; }
            QLabel#Title { font-size: 24px; font-weight: bold; color: #2c3e50; }
            QListWidget { border: none; background: transparent; }
            QPushButton#Primary { background-color: #3498db; color: white; border-radius: 10px; padding: 10px; font-weight: bold; }
            QPushButton#Primary:hover { background-color: #2980b9; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("CrossLink")
        header.setObjectName("Title")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        ip_info = QLabel(f"My IP: {self.protocol.get_local_ip()}")
        ip_info.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        ip_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(ip_info)

        # Device List
        layout.addWidget(QLabel("<b>Nearby Devices</b>"))
        self.device_list = QListWidget()
        layout.addWidget(self.device_list)

        # Progress
        self.progress_container = QFrame()
        self.progress_container.setVisible(False)
        prog_layout = QVBoxLayout(self.progress_container)
        self.prog_label = QLabel("Transferring...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #ddd; border-radius: 5px; text-align: center; } QProgressBar::chunk { background-color: #3498db; }")
        prog_layout.addWidget(self.prog_label)
        prog_layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_container)

        # Footer
        footer = QLabel("CrossLink v2.0 Standalone")
        footer.setStyleSheet("color: #bdc3c7; font-size: 10px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        # Enable Drag & Drop
        self.setAcceptDrops(True)

    def setup_signals(self):
        self.device_signal.connect(self.update_devices)
        self.progress_signal.connect(self.update_progress)
        self.file_signal.connect(self.notify_file)

    @Slot(dict)
    def update_devices(self, devices):
        self.device_list.clear()
        for ip, name in devices.items():
            item = QListWidgetItem(self.device_list)
            widget = DeviceItem(name, ip)
            item.setSizeHint(widget.sizeHint())
            self.device_list.setItemWidget(item, widget)
            widget.send_btn.clicked.connect(lambda checked, i=ip: self.pick_and_send(i))

    def pick_and_send(self, target_ip):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Send")
        if file_path:
            self.protocol.send_file(target_ip, file_path)

    @Slot(str, int, int)
    def update_progress(self, filename, current, total):
        self.progress_container.setVisible(True)
        self.prog_label.setText(f"File: {filename}")
        val = int((current / total) * 100)
        self.progress_bar.setValue(val)
        if val >= 100:
            self.prog_label.setText("Transfer Complete!")
            # Hide after 3 seconds
            from PySide6.QtCore import QTimer
            QTimer.singleShot(3000, lambda: self.progress_container.setVisible(False))

    @Slot(str)
    def notify_file(self, filename):
        print(f"DEBUG: File received: {filename}")
        # In a real app, show a system notification
        self.prog_label.setText(f"Received: {filename}")
        self.progress_container.setVisible(True)
        self.progress_bar.setValue(100)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.progress_container.setVisible(False))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if self.device_list.count() == 0:
            return
            
        # Default to the first device in the list for simplicity in drop
        target_ip = self.device_list.itemWidget(self.device_list.item(0)).ip
        
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                self.protocol.send_file(target_ip, file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CrossLinkGUI()
    window.show()
    sys.exit(app.exec())
