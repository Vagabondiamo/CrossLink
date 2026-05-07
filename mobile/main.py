import sys
import os
from pathlib import Path
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.utils import platform
from kivy.clock import Clock

# Reimportazione robusta del protocollo
try:
    from protocol import CrossLinkProtocol
except ImportError:
    CrossLinkProtocol = None

class CrossLinkApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.status_label = Label(text="Inizializzazione...", size_hint_y=0.2)
        self.layout.add_widget(self.status_label)
        
        # Area dispositivi scoperti
        self.devices_scroll = ScrollView()
        self.devices_grid = GridLayout(cols=1, size_hint_y=None)
        self.devices_grid.bind(minimum_height=self.devices_grid.setter('height'))
        self.devices_scroll.add_widget(self.devices_grid)
        self.layout.add_widget(self.devices_scroll)
        
        try:
            if CrossLinkProtocol:
                upload_dir = "/sdcard/Download/CrossLink" if platform == 'android' else "uploads"
                self.protocol = CrossLinkProtocol(upload_dir=upload_dir)
                
                # Callback
                self.protocol.on_device_discovered = self.update_devices_ui
                self.protocol.on_file_received = lambda f: Clock.schedule_once(lambda dt: self.status_label.set_text(f"Ricevuto: {f}"))
                
                # Avvio
                self.protocol.start_discovery()
                self.status_label.text = f"Protocollo Caricato!\nDevice: {self.protocol.device_name}\nRicerca dispositivi..."
            else:
                self.status_label.text = "Errore: Modulo protocollo non trovato"
        except Exception as e:
            self.status_label.text = f"Errore Critico:\n{str(e)}"
            
        return self.layout

    def update_devices_ui(self, devices):
        Clock.schedule_once(lambda dt: self._refresh_grid(devices))

    def _refresh_grid(self, devices):
        self.devices_grid.clear_widgets()
        for ip, name in devices.items():
            btn = Button(text=f"{name}\n{ip}", size_hint_y=None, height=100)
            self.devices_grid.add_widget(btn)

    def on_start(self):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            except:
                pass

if __name__ == '__main__':
    CrossLinkApp().run()
