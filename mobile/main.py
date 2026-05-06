import sys
import os
from pathlib import Path

# On Android, protocol.py is in the same folder as main.py
try:
    from protocol import CrossLinkProtocol
except ImportError:
    # Fallback for local PC testing if structure is different
    sys.path.append(str(Path(__file__).parent.parent))
    from protocol import CrossLinkProtocol

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import QLabel
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.utils import platform

class CrossLinkMobile(App):
    def build(self):
        # Determine a safe storage path
        if platform == 'android':
            from android.storage import primary_external_storage_path
            primary_storage = primary_external_storage_path()
            upload_path = os.path.join(primary_storage, "Download", "CrossLink")
        else:
            upload_path = "mobile_uploads"

        try:
            self.protocol = CrossLinkProtocol(upload_dir=upload_path)
        except Exception as e:
            # If we can't create the dir, fallback to app private storage
            print(f"Failed to create upload dir: {e}")
            self.protocol = CrossLinkProtocol(upload_dir=self.user_data_dir)

        self.protocol.on_device_discovered = self.on_devices
        self.protocol.on_transfer_progress = self.on_progress
        self.protocol.on_file_received = self.on_received

        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Header
        self.main_layout.add_widget(QLabel(text="CrossLink Mobile", font_size='24sp', size_hint_y=None, height=100))
        
        local_ip = "Unknown"
        try:
            local_ip = self.protocol.get_local_ip()
        except:
            pass
            
        self.ip_label = QLabel(text=f"My IP: {local_ip}", size_hint_y=None, height=50)
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

        try:
            self.protocol.start_discovery()
            self.protocol.start_server()
        except Exception as e:
            self.status_label.text = f"Error starting server: {e}"
        
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
            percent = int((current/total)*100) if total > 0 else 0
            self.status_label.text = f"Transferring {filename}: {percent}%"
        Clock.schedule_once(_update)

    def on_received(self, filename):
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', f"Received: {filename}"))

    def send_test_file(self, ip):
        self.status_label.text = f"Attempting to send to {ip}..."
        # Simplified for now
        self.status_label.text = "Click to send simulated file (Not implemented yet)"

if __name__ == '__main__':
    CrossLinkMobile().run()
