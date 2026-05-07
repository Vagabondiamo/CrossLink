import socket
import threading
import os
import json
import time
from pathlib import Path

class CrossLinkProtocol:
    UDP_PORT = 18790
    TCP_PORT = 18791
    BUFFER_SIZE = 1024 * 64 # 64KB chunks
    
    def __init__(self, upload_dir="uploads"):
        self.upload_dir = Path(upload_dir)
        try:
            self.upload_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Directory creation failed: {e}")
            
        try:
            self.device_name = socket.gethostname()
        except:
            self.device_name = "Android-Device"
            
        self.discovered_devices = {} # {ip: name}
        self.is_running = True
        self.on_file_received = None # Callback(filename)
        self.on_device_discovered = None # Callback(devices_dict)
        self.on_transfer_progress = None # Callback(filename, current, total)
        print(f"DEBUG: CrossLinkProtocol initialized as {self.device_name}")

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Connessione a un IP pubblico per determinare l'interfaccia locale
            s.connect(('8.8.8.8', 80))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    # --- Discovery (UDP) ---
    def start_discovery(self):
        print("DEBUG: Starting discovery threads...")
        threading.Thread(target=self._udp_broadcaster, daemon=True).start()
        threading.Thread(target=self._udp_listener, daemon=True).start()

    def _udp_broadcaster(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        while self.is_running:
            try:
                ip = self.get_local_ip()
                message = json.dumps({"type": "discovery", "name": self.device_name, "ip": ip}).encode()
                
                # Prova sia il broadcast universale che quello specifico della tua rete WiFi
                sock.sendto(message, ('255.255.255.255', self.UDP_PORT))
                sock.sendto(message, ('192.168.170.255', self.UDP_PORT))
                
            except Exception as e:
                print(f"DEBUG: Broadcast error: {e}")
            time.sleep(3)

    def _udp_listener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.UDP_PORT)) 
        print("DEBUG: Listening for discovery packets...")
        
        while self.is_running:
            try:
                data, addr = sock.recvfrom(1024)
                msg = json.loads(data.decode())
                # print(f"DEBUG: Received message from {addr}: {msg}")
                if msg["type"] == "discovery" and msg["ip"] != self.get_local_ip():
                    if msg["ip"] not in self.discovered_devices:
                        print(f"DEBUG: Discovered new device: {msg['name']} ({msg['ip']})")
                        self.discovered_devices[msg["ip"]] = msg["name"]
                        if self.on_device_discovered:
                            self.on_device_discovered(self.discovered_devices)
            except Exception as e:
                # print(f"DEBUG: Listener error: {e}")
                pass

    # --- Transfer (TCP) ---
    def start_server(self):
        threading.Thread(target=self._tcp_server, daemon=True).start()

    def _tcp_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Fix: Usiamo la costante corretta SOL_SOCKET dall'oggetto socket
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', self.TCP_PORT))
        server.listen(5)
        while self.is_running:
            client, addr = server.accept()
            threading.Thread(target=self._handle_receive, args=(client,), daemon=True).start()

    def _handle_receive(self, client):
        try:
            header_data = client.recv(1024).decode()
            header = json.loads(header_data)
            
            if header["type"] == "file":
                filename = header["filename"]
                filesize = header["size"]
                save_path = self.upload_dir / filename
                
                with open(save_path, "wb") as f:
                    received = 0
                    while received < filesize:
                        chunk = client.recv(self.BUFFER_SIZE)
                        if not chunk: break
                        f.write(chunk)
                        received += len(chunk)
                        if self.on_transfer_progress:
                            self.on_transfer_progress(filename, received, filesize)
                client.close()
                if self.on_file_received:
                    self.on_file_received(filename)
        except Exception as e:
            print(f"DEBUG: Receive error: {e}")
            
    def stop(self):
        self.is_running = False
