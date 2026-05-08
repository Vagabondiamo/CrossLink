<div align="center">

<pre>
 ██████╗██████╗  ██████╗ ███████╗███████╗      ██╗     ██╗███╗   ██╗██╗  ██╗
██╔════╝██╔══██╗██╔═══██╗██╔════╝██╔════╝      ██║     ██║████╗  ██║██║ ██╔╝
██║     ██████╔╝██║   ██║███████╗███████╗█████╗██║     ██║██╔██╗ ██║█████╔╝ 
██║     ██╔══██╗██║   ██║╚════██║╚════██║╚════╝██║     ██║██║╚██╗██║██╔═██╗ 
╚██████╗██║  ██║╚██████╔╝███████║███████║      ███████╗██║██║ ╚████║██║  ██╗
 ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝      ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
</pre>

**Transfer files between PC and phone in seconds — no app, no cable, no cloud.**

Start the server, scan the QR with your camera, and you're ready to go.

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

</div>

---

## How it works

CrossLink starts a lightweight local web server on your PC and prints a **QR code** directly in the terminal. Anyone on the same Wi-Fi network can scan it with their phone camera — no app needed — and instantly open a clean web interface to:

- 📤 **Send files to the PC** — select one or more files from your phone, watch the real-time progress bar, and they land directly in the folder where you started the server
- 📥 **Download files from the PC** — browse the list of files in the current folder and download any of them with one tap

> ⚡ Works on Wi-Fi networks **without internet access** — isolated routers, mobile hotspots, and local-only setups all work fine.

---

## Requirements

- Python 3.8 or higher
- The following Python libraries:

```
fastapi
uvicorn
segno
python-multipart
```

Install them all at once:

```bash
pip install fastapi uvicorn segno python-multipart
```

---

## Installation

```bash
git clone https://github.com/Vagabondiamo/CrossLink.git
cd CrossLink
pip install fastapi uvicorn segno python-multipart
```

---

## Quick launch (Linux/macOS)

Instead of running `python server.py` every time, you can use the included `crosslink` script to launch the server from anywhere with a single command:

```bash
# Make it executable (only once)
chmod +x crosslink

# Move it to your PATH (only once)
sudo mv crosslink /usr/local/bin/
```

From now on, just navigate to any folder and run:

```bash
crosslink
```

---

## Usage

### Send a file **from phone to PC**

1. Open a terminal in the folder where you want to receive files
2. Start the server:
   ```bash
   python server.py
   ```
   Or, if you set up the quick launch:
   ```bash
   crosslink
   ```
3. A QR code will appear in the terminal along with a message like:
   ```
   Server running at http://192.168.1.10:8000
   ```
4. Scan the QR code with your phone camera
5. Tap the upload area, select one or more files, and press **Upload**
6. A progress bar will show the transfer status — files are saved in the folder where you started the server

---

### Send a file **from PC to phone**

1. Navigate to the folder containing the file you want to send:
   ```bash
   cd /path/to/your/folder
   ```
2. Start the server:
   ```bash
   python server.py
   ```
   Or with the quick launch:
   ```bash
   crosslink
   ```
3. Scan the QR code with your phone
4. In the **"Files on PC"** section, you'll see all files in the current folder — tap **Download** on the one you want

---

## Project structure

```
CrossLink/
├── server.py        # Web server (FastAPI) + QR code generation + mobile UI
├── gui.py           # Optional desktop GUI (PySide6)
├── protocol.py      # Shared communication logic
├── mobile/          # Alternative mobile client (Kivy)
└── crosslink        # Quick-launch script (Linux/macOS)
```

---

## Security notes

CrossLink is designed for **local and private use**. The server is accessible to **any device on the same network**, so:

- Avoid running it on public networks (cafés, airports, etc.) — use your **phone's personal hotspot** instead: CrossLink works perfectly on it even without an internet connection, and only your devices will be on the network
- Avoid running it in your home directory or in folders with sensitive data
- Stop the server with `Ctrl+C` when you're done

---

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
