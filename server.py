import os
import socket
import uvicorn
import signal
import sys
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import segno
from pathlib import Path
from datetime import datetime

# Gestione uscita pulita
def signal_handler(sig, frame):
    print("\n[!] Server Stoped.")
    print("================================================================================")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

app = FastAPI()

# Configuration
# Condividiamo la cartella corrente da cui viene lanciato lo script
UPLOAD_DIR = Path(os.getcwd())

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CrossLink - Transfer</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gradient-to-br from-blue-500 to-indigo-700 min-h-screen flex flex-col items-center p-4 text-white font-sans">
        <h1 class="text-3xl font-bold mt-8 mb-4">CrossLink</h1>
        
        <main class="w-full max-w-2xl bg-white/10 backdrop-blur-md rounded-3xl p-8 shadow-2xl">
            <h2 class="text-xl font-bold mb-4">Send to PC</h2>
            <div class="flex gap-4">
                <button onclick="document.getElementById('file-input').click()" class="flex-1 bg-white/20 p-4 rounded-xl hover:bg-white/30 transition">Select Files</button>
                <button onclick="document.getElementById('dir-input').click()" class="flex-1 bg-white/20 p-4 rounded-xl hover:bg-white/30 transition">Select Folder</button>
            </div>
            
            <input type="file" id="file-input" class="hidden" multiple>
            <input type="file" id="dir-input" class="hidden" webkitdirectory directory>
            
            <div id="selection-area" class="mt-4 space-y-2"></div>

            <button id="upload-btn" class="w-full mt-6 bg-indigo-600 text-white font-bold py-3 rounded-xl shadow-lg transition-all hidden">
                Upload Selected
            </button>
            
            <div id="progress-container" class="mt-6 hidden">
                <div class="w-full bg-gray-200 rounded-full h-4">
                    <div id="progress-bar" class="bg-indigo-600 h-4 rounded-full" style="width: 0%"></div>
                </div>
                <p id="progress-text" class="text-center mt-2 text-sm">0%</p>
            </div>

            <h2 class="text-xl font-bold mt-10 mb-4">Files on PC</h2>
            <div id="pc-files" class="bg-white/5 rounded-xl p-4 max-h-60 overflow-y-auto">
                <ul id="files-list" class="space-y-2 text-sm"></ul>
            </div>
        </main>

        <script>
            const fileInput = document.getElementById('file-input');
            const dirInput = document.getElementById('dir-input');
            const selectionArea = document.getElementById('selection-area');
            const uploadBtn = document.getElementById('upload-btn');
            const filesList = document.getElementById('files-list');
            const progressBar = document.getElementById('progress-bar');
            const progressText = document.getElementById('progress-text');
            const progressContainer = document.getElementById('progress-container');

            let selectedFiles = [];

            function renderSelection() {
                selectionArea.innerHTML = '';
                selectedFiles.forEach((file, index) => {
                    const div = document.createElement('div');
                    div.className = 'flex justify-between items-center bg-white/10 p-2 rounded-lg text-sm';
                    div.innerHTML = `
                        <span class="truncate">${file.webkitRelativePath || file.name}</span>
                        <button onclick="removeFile(${index})" class="text-red-400 hover:text-red-300 ml-2 font-bold px-2">X</button>
                    `;
                    selectionArea.appendChild(div);
                });
                
                uploadBtn.classList.toggle('hidden', selectedFiles.length === 0);
            }

            function removeFile(index) {
                selectedFiles.splice(index, 1);
                renderSelection();
            }

            function handleFileSelection(files) {
                Array.from(files).forEach(file => selectedFiles.push(file));
                renderSelection();
            }

            fileInput.onchange = (e) => handleFileSelection(e.target.files);
            dirInput.onchange = (e) => handleFileSelection(e.target.files);

            uploadBtn.onclick = async () => {
                const formData = new FormData();
                selectedFiles.forEach(file => {
                    formData.append('files', file, file.webkitRelativePath || file.name);
                });
                
                uploadBtn.classList.add('hidden');
                progressContainer.classList.remove('hidden');

                const xhr = new XMLHttpRequest();
                xhr.open('POST', '/upload', true);
                xhr.upload.onprogress = (e) => {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    progressBar.style.width = percent + '%';
                    progressText.innerText = percent + '%';
                };
                xhr.onload = () => {
                    progressText.innerText = 'Upload Completato!';
                    setTimeout(() => {
                        progressContainer.classList.add('hidden');
                        selectedFiles = [];
                        renderSelection();
                        refreshFiles();
                    }, 2000);
                };
                xhr.send(formData);
            };

            async function refreshFiles() {
                const res = await fetch('/files');
                const data = await res.json();
                filesList.innerHTML = '';
                data.forEach(filename => {
                    const li = document.createElement('li');
                    li.className = 'flex justify-between items-center border-b border-white/10 pb-2';
                    li.innerHTML = `<span>${filename}</span> <a href="/download/${filename}" class="bg-white/20 px-3 py-1 rounded-lg text-xs hover:bg-white/30">Download</a>`;
                    filesList.appendChild(li);
                });
            }
            refreshFiles();
        </script>
    </body>
    </html>
    """

@app.post("/upload")
async def upload_files(request: Request):
    form = await request.form()
    files = form.getlist("files")
    for file in files:
        filename = file.filename
        save_path = UPLOAD_DIR / filename
        save_path.parent.mkdir(parents=True, exist_ok=True)
        contents = await file.read()
        with open(save_path, "wb") as f:
            f.write(contents)
        print(f"DEBUG: Received [{filename}]")
    return {"status": "success"}

@app.get("/files")
async def list_files():
    file_list = []
    try:
        for item in UPLOAD_DIR.iterdir():
            if item.is_file():
                file_list.append(item.name)
    except Exception as e:
        print(f"DEBUG: List files error: {e}")
    return file_list

@app.get("/download/{filename:path}")
async def download_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File non trovato")
    return FileResponse(file_path, filename=os.path.basename(filename))

if __name__ == "__main__":
    ip = get_ip_address()
    url = f"http://{ip}:8000"
    
    banner = f"""
================================================================================
 ██████╗██████╗  ██████╗ ███████╗███████╗      ██╗     ██╗███╗   ██╗██╗  ██╗
██╔════╝██╔══██╗██╔═══██╗██╔════╝██╔════╝      ██║     ██║████╗  ██║██║ ██╔╝
██║     ██████╔╝██║   ██║███████╗███████╗█████╗██║     ██║██╔██╗ ██║█████╔╝ 
██║     ██╔══██╗██║   ██║╚════██║╚════██║╚════╝██║     ██║██║╚██╗██║██╔═██╗ 
╚██████╗██║  ██║╚██████╔╝███████║███████║      ███████╗██║██║ ╚████║██║  ██╗
 ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝      ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
================================================================================
 PC Address: {url}
 SCAN THIS QR CODE ON YOUR PHONE:
"""
    print(banner)
    
    qr = segno.make(url)
    qr.terminal(border=1, compact=True)
    print("================================================================================")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
