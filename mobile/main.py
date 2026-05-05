import sys
import os
from pathlib import Path

# Add parent dir to path to import protocol
sys.path.append(str(Path(__file__).parent.parent))
from protocol import CrossLinkProtocol

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import QLabel
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.core.window import Window

class CrossLinkMobile(App):
    def build(self):
        self.protocol = CrossLinkProtocol(upload_dir="/sdcard/Download/CrossLink")
        # For testing on PC, use a local dir
        if not os.path.exists("/sdcard"):
            self.protocol.upload_dir = Path("mobile_uploads")
            self.protocol.upload_dir.mkdir(exist_ok=True)

        self.protocol.on_device_discovered = self.on_devices
        self.protocol.on_transfer_progress = self.on_progress
        self.protocol.on_file_received = self.on_received

        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Header
        self.main_layout.add_widget(QLabel(text="CrossLink Mobile", font_size='24sp', size_hint_y=None, height=100))
        self.ip_label = QLabel(text=f"My IP: {self.protocol.get_local_ip()}", size_hint_y=None, height=50)
        self.main_layout.add_widget(self.ip_label)

        # Device List
        self.main_layout.add_widget(QLabel(text="Nearby PC Devices:", size_hint_y=None, height=50))
        self.scroll = ScrollView()
        self.device_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.device_grid.bind(minimum_height=self.device_grid.setter('height'))
        self.scroll.add_widget(self.device_grid)
        self.main_layout.add_widget(self.scroll)

        # Progress
        self.status_label = QLabel(text="Waiting for connections...", size_hint_y=None, height=100)
        self.main_layout.add_widget(self.status_label)

        self.protocol.start_discovery()
        self.protocol.start_server()
        
        return self.main_layout

    def on_devices(self, devices):
        Clock.schedule_once(lambda dt: self._update_device_list(devices))

    def _update_device_list(self, devices):
        self.device_grid.clear_widgets()
        for ip, name in devices.items():
            btn = Button(text=f"{name}\n({ip})", size_hint_y=None, height=150)
            btn.bind(on_release=lambda x, i=ip: self.send_test_file(i))
            self.device_grid.add_widget(btn)

    def on_progress(self, filename, current, total):
        def _update(dt):
            percent = int((current/total)*100)
            self.status_label.text = f"Transferring {filename}: {percent}%"
        Clock.schedule_once(_update)

    def on_received(self, filename):
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', f"Received: {filename}"))

    def send_test_file(self, ip):
        # In a real app, use a file chooser. For now, we'll try to find a sample image or file.
        self.status_label.text = f"Attempting to send to {ip}..."
        # In Android, we'd use a native file picker. 
        # Here we just show the intent.
        self.status_label.text = "Click to send simulated file (Not implemented yet)"

if __name__ == '__main__':
    CrossLinkMobile().run()
