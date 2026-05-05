# CrossLink Standalone

Cross-platform file transfer application (PC & Mobile) that works without a web browser.

## Features
- **Auto-Discovery:** Devices find each other automatically on the same Wi-Fi.
- **Native GUI:** Professional interface using PySide6 (PC) and Kivy (Mobile).
- **Socket Transfer:** High-speed transfers using a custom TCP protocol.
- **Drag & Drop:** Send files to the first discovered device by dragging them into the PC window.

## How to use on PC
1. Navigate to the project folder:
   ```bash
   cd ~/Scrivania/crosslink_standalone
   ```
2. Run the application:
   ```bash
   ./venv/bin/python gui.py
   ```

## How to use on Mobile (Android)
1. Install **Pydroid 3** or **Termux** from the Play Store.
2. Copy the `crosslink_standalone` folder to your phone.
3. Install dependencies (`pip install kivy`).
4. Run `mobile/main.py`.

## Directory structure
- `protocol.py`: Shared communication logic.
- `gui.py`: Desktop application (PySide6).
- `mobile/`: Mobile application source (Kivy).
- `uploads/`: Default folder for received files.
