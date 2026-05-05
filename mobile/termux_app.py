import sys
import os
import json
import socket
from pathlib import Path

# Aggiunge la cartella superiore al path per caricare il protocollo
sys.path.append(str(Path(__file__).parent.parent))
from protocol import CrossLinkProtocol

def clear_console():
    os.system('clear' if os.name == 'posix' else 'cls')

class CrossLinkTermux:
    def __init__(self):
        # Su Termux i file vengono salvati nei Download condivisi
        self.download_path = Path("/sdcard/Download/CrossLink")
        try:
            self.download_path.mkdir(parents=True, exist_ok=True)
        except:
            self.download_path = Path("received_files")
            self.download_path.mkdir(exist_ok=True)
            
        self.protocol = CrossLinkProtocol(upload_dir=self.download_path)
        self.protocol.on_device_discovered = self.refresh_devices
        self.protocol.on_file_received = self.notify_received
        self.protocol.on_transfer_progress = self.show_progress
        
        self.devices = {}

    def refresh_devices(self, devices):
        self.devices = devices

    def notify_received(self, filename):
        print(f"\n[✅] Ricevuto: {filename}")
        print(f"[📍] Salvato in: {self.download_path}")
        self.print_menu()

    def show_progress(self, filename, current, total):
        percent = int((current/total)*100)
        sys.stdout.write(f"\r[🚀] {filename}: [{'#'*(percent//5)}{'-'*(20-(percent//5))}] {percent}%")
        sys.stdout.flush()
        if percent >= 100: print()

    def print_menu(self):
        clear_console()
        print("="*40)
        print("   CROSSLINK - TERMUX EDITION   ")
        print("="*40)
        print(f"IP Locale: {self.protocol.get_local_ip()}")
        print(f"Cartella:  {self.download_path}")
        print("-"*40)
        print("Dispositivi trovati:")
        if not self.devices:
            print("  (In cerca di PC sulla rete...)")
        else:
            for i, (ip, name) in enumerate(self.devices.items()):
                print(f"  {i+1}. {name} ({ip})")
        print("-"*40)
        print("COMANDI:")
        print("  [numero] - Invia un file al dispositivo")
        print("  r        - Aggiorna lista")
        print("  q        - Esci")
        print("-"*40)

    def run(self):
        self.protocol.start_discovery()
        self.protocol.start_server()
        
        while True:
            self.print_menu()
            choice = input("\nScegli: ").lower()
            
            if choice == 'q':
                self.protocol.stop()
                break
            elif choice == 'r':
                continue
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(self.devices):
                    target_ip = list(self.devices.keys())[idx]
                    file_to_send = input("Percorso del file da inviare: ")
                    if os.path.exists(file_to_send):
                        self.protocol.send_file(target_ip, file_to_send)
                    else:
                        print("File non trovato!")
                        time.sleep(2)
            else:
                print("Scelta non valida")
                time.sleep(1)

if __name__ == "__main__":
    app = CrossLinkTermux()
    app.run()
