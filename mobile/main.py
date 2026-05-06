import sys
import os
import traceback
from pathlib import Path

# On Android, protocol.py is in the same folder as main.py
try:
    from protocol import CrossLinkProtocol
except ImportError:
    # Fallback for local PC testing if structure is different
    try:
        sys.path.append(str(Path(__file__).parent.parent))
        from protocol import CrossLinkProtocol
    except:
        CrossLinkProtocol = None

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
        try:
            return self._actual_build()
        except Exception as e:
            error_msg = f"CRITICAL STARTUP ERROR:\n{traceback.format_exc()}"
            print(error_msg)
            return QLabel(text=error_msg, font_size='14sp', color=(1, 0, 0, 1), 
                          text_size=(800, None), halign='left', valign='top')

    def _actual_build(self):
        # Determine a safe storage path
        upload_path = self.user_data_dir # Default safe path
        
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            
            try:
                from android.storage import primary_external_storage_path
                primary_storage = primary_external_storage_path()
                if primary_storage:
                    upload_path = os.path.join(primary_storage, "Download", "CrossLink")
            except Exception as e:
                print(f"Android storage API failed: {e}")

        if CrossLinkProtocol is None:
            raise ImportError("Could not load protocol.py. Make sure it was copied to the mobile/ folder.")

        try:
            self.protocol = CrossLinkProtocol(upload_dir=upload_path)
        except Exception as e:
            # Final fallback to app private storage
            print(f"Failed to create preferred upload dir: {e}")
            self.protocol = CrossLinkProtocol(upload_dir=self.user_data_dir)

        self.protocol.on_device_discovered = self.on_devices
        self.protocol.on_transfer_progress = self.on_progress
        self.protocol.on_file_received = self.on_received

        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Header
        self.main_layout.add_widget(QLabel(text="CrossLink Mobile v0.2", font_size='24sp', size_hint_y=None, height=100))
        
        local_ip = "Unknown"
        try:
            local_ip = self.protocol.get_local_ip()
        except:
            pass
            
        self.ip_label = QLabel(text=f"My IP: {local_ip}\nSave to: {self.protocol.upload_dir}", 
                               size_hint_y=None, height=100, font_size='14sp')
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
