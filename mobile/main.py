import sys
import os

# Prepariamo un logger che non dipenda dal disco se possibile
from kivy.logger import Logger
Logger.info("CrossLink: Starting minimal boot sequence")

try:
    # Importazione protetta del protocollo
    try:
        import protocol
        Logger.info("CrossLink: Protocol module imported")
    except Exception as e:
        Logger.error(f"CrossLink: Protocol import failed: {e}")
        protocol = None

    from kivy.app import App
    from kivy.uix.label import QLabel
    from kivy.uix.boxlayout import BoxLayout
    from kivy.utils import platform

    class CrossLinkMobile(App):
        def build(self):
            Logger.info("CrossLink: build() called")
            layout = BoxLayout(orientation='vertical')
            
            title = QLabel(text="CrossLink Minimal v0.4", font_size='30sp')
            info = QLabel(text=f"Platform: {platform}\nStatus: Ready")
            
            layout.add_widget(title)
            layout.add_widget(info)
            
            if protocol is None:
                layout.add_widget(QLabel(text="ERROR: protocol.py not found!", color=(1,0,0,1)))
            else:
                try:
                    # Inizializzazione minima senza percorsi strani
                    p = protocol.CrossLinkProtocol(upload_dir=self.user_data_dir)
                    layout.add_widget(QLabel(text=f"IP: {p.get_local_ip()}"))
                    Logger.info("CrossLink: Protocol initialized")
                except Exception as e:
                    layout.add_widget(QLabel(text=f"Protocol Init Error: {e}", color=(1,0,1,1)))
            
            return layout

    if __name__ == '__main__':
        Logger.info("CrossLink: Running App")
        CrossLinkMobile().run()

except Exception as e:
    import traceback
    Logger.error(f"CrossLink: FATAL CRASH:\n{traceback.format_exc()}")
