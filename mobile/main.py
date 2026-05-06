import sys
import os
import traceback
from pathlib import Path

# --- SISTEMA DI LOG ESTREMO ---
DEBUG_FILE = "/sdcard/Download/crosslink_debug.txt"

def log_debug(msg):
    try:
        with open(DEBUG_FILE, "a") as f:
            import datetime
            now = datetime.datetime.now().strftime("%H:%M:%S")
            f.write(f"[{now}] {msg}\n")
    except:
        pass

# Pulisci log precedente
try:
    if os.path.exists(DEBUG_FILE):
        os.remove(DEBUG_FILE)
except:
    pass

log_debug(">>> SCRIPT STARTING")

try:
    from protocol import CrossLinkProtocol
    log_debug("Protocol imported successfully")
except Exception as e:
    log_debug(f"CRITICAL: Protocol import failed: {e}")
    CrossLinkProtocol = None

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import QLabel
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.utils import platform

log_debug(f"Platform detected: {platform}")

class CrossLinkMobile(App):
    def build(self):
        log_debug("Entering build()")
        try:
            return self._actual_build()
        except Exception as e:
            err = traceback.format_exc()
            log_debug(f"FATAL ERROR IN BUILD:\n{err}")
            return QLabel(text=f"FATAL ERROR (check Download/crosslink_debug.txt):\n{err[:500]}", 
                          font_size='12sp', color=(1, 0, 0, 1))

    def _actual_build(self):
        upload_path = self.user_data_dir
        log_debug(f"User data dir: {upload_path}")
        
        if platform == 'android':
            log_debug("Requesting permissions...")
            try:
                from android.permissions import request_permissions, Permission
                # Chiediamo i permessi ma non blocchiamo l'esecuzione
                request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            except Exception as e:
                log_debug(f"Permission request failed (non-fatal): {e}")

        if CrossLinkProtocol is None:
            raise ImportError("protocol.py is missing or corrupted!")

        self.protocol = CrossLinkProtocol(upload_dir=upload_path)
        log_debug("Protocol instance created")

        self.protocol.on_device_discovered = self.on_devices
        self.protocol.on_transfer_progress = self.on_progress
        self.protocol.on_file_received = self.on_received

        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.main_layout.add_widget(QLabel(text="CrossLink Debug v0.3", font_size='24sp', size_hint_y=None, height=100))
        
        try:
            local_ip = self.protocol.get_local_ip()
            log_debug(f"Local IP: {local_ip}")
        except:
            local_ip = "Unknown"
            
        self.ip_label = QLabel(text=f"IP: {local_ip}\nLogs: {DEBUG_FILE}", size_hint_y=None, height=100)
        self.main_layout.add_widget(self.ip_label)

        self.scroll = ScrollView()
        self.device_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.device_grid.bind(minimum_height=self.device_grid.setter('height'))
        self.scroll.add_widget(self.device_grid)
        self.main_layout.add_widget(self.scroll)

        self.status_label = QLabel(text="System ready. Waiting...", size_hint_y=None, height=100)
        self.main_layout.add_widget(self.status_label)

        log_debug("Starting server and discovery...")
        try:
            self.protocol.start_discovery()
            self.protocol.start_server()
            log_debug("Server/Discovery threads started")
        except Exception as e:
            log_debug(f"Server start failed: {e}")
        
        return self.main_layout

    def on_devices(self, devices):
        Clock.schedule_once(lambda dt: self._update_device_list(devices))

    def _update_device_list(self, devices):
        self.device_grid.clear_widgets()
        for ip, name in devices.items():
            btn = Button(text=f"{name}\n({ip})", size_hint_y=None, height=150)
            self.device_grid.add_widget(btn)

    def on_progress(self, filename, current, total):
        pass

    def on_received(self, filename):
        log_debug(f"File received: {filename}")
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', f"Received: {filename}"))

if __name__ == '__main__':
    try:
        log_debug("Calling CrossLinkMobile().run()")
        CrossLinkMobile().run()
    except Exception as e:
        log_debug(f"CRASH IN MAIN LOOP:\n{traceback.format_exc()}")
