import sys
import os
import traceback
from pathlib import Path
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import platform

# Reimportazione robusta del protocollo
try:
    from protocol import CrossLinkProtocol
except ImportError:
    CrossLinkProtocol = None

class CrossLinkApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.status_label = Label(text="Inizializzazione...", font_size='18sp')
        self.layout.add_widget(self.status_label)
        
        try:
            if CrossLinkProtocol:
                # Usa una cartella sicura per i test su Android
                if platform == 'android':
                    upload_dir = "/sdcard/Download/CrossLink"
                else:
                    upload_dir = "uploads"
                    
                self.protocol = CrossLinkProtocol(upload_dir=upload_dir)
                self.status_label.text = f"Protocollo Caricato!\nDevice: {self.protocol.device_name}"
            else:
                self.status_label.text = "Errore: Modulo protocollo non trovato"
        except Exception as e:
            self.status_label.text = f"Errore Critico:\n{str(e)}"
            
        return self.layout

    def on_start(self):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            except:
                pass

if __name__ == '__main__':
    CrossLinkApp().run()
