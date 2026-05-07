import os
import socket
import uvicorn
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import segno
from pathlib import Path
from datetime import datetime

app = FastAPI()

# Configuration
# Condividiamo la cartella corrente da cui viene lanciato lo script
UPLOAD_DIR = Path(os.getcwd())

upload_history = []

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
        <title>CrossLink - File Transfer</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gradient-to-br from-blue-500 to-indigo-700 min-h-screen flex flex-col items-center p-4 text-white font-sans">
        <h1 class="text-3xl font-bold mt-8 mb-4">CrossLink</h1>
        
        <main class="w-full max-w-2xl bg-white/10 backdrop-blur-md rounded-3xl p-8 shadow-2xl">
            <h2 class="text-xl font-bold mb-4">Send to PC</h2>
            <div id="drop-zone" class="border-2 border-dashed border-indigo-200 rounded-2xl p-10 flex flex-col items-center justify-center cursor-pointer hover:border-indigo-400 transition-colors">
                <p id="drop-text" class="text-sm font-medium">Tap to select files</p>
                <input type="file" id="file-input" class="hidden" multiple>
            </div>
            
            <div id="progress-container" class="mt-6 hidden">
                <div class="w-full bg-gray-200 rounded-full h-4">
                    <div id="progress-bar" class="bg-indigo-600 h-4 rounded-full" style="width: 0%"></div>
                </div>
                <p id="progress-text" class="text-center mt-2 text-sm">0%</p>
            </div>

            <button id="upload-btn" class="w-full mt-6 bg-indigo-600 text-white font-bold py-3 rounded-xl shadow-lg transition-all hidden">
                Upload
            </button>

            <h2 class="text-xl font-bold mt-10 mb-4">Files on PC</h2>
            <div id="pc-files" class="bg-white/5 rounded-xl p-4 max-h-60 overflow-y-auto">
                <ul id="files-list" class="space-y-2 text-sm"></ul>
            </div>
        </main>

        <script>
            const fileInput = document.getElementById('file-input');
            const dropZone = document.getElementById('drop-zone');
            const dropText = document.getElementById('drop-text');
            const uploadBtn = document.getElementById('upload-btn');
            const progressContainer = document.getElementById('progress-container');
            const progressBar = document.getElementById('progress-bar');
            const progressText = document.getElementById('progress-text');
            const filesList = document.getElementById('files-list');

            dropZone.onclick = () => fileInput.click();
            
            fileInput.onchange = (e) => {
                if (e.target.files.length > 0) {
                    dropText.innerText = Array.from(e.target.files).map(f => f.name).join(', ');
                    uploadBtn.classList.remove('hidden');
                }
            };

            uploadBtn.onclick = async () => {
                const formData = new FormData();
                for (const file of fileInput.files) formData.append('files', file);
                
                uploadBtn.classList.add('hidden');
                progressContainer.classList.remove('hidden');

                const xhr = new XMLHttpRequest();
                xhr.open('POST', '/upload', true);
                
                xhr.upload.onprogress = (e) => {
                    if (e.lengthComputable) {
                        const percent = Math.round((e.loaded / e.total) * 100);
                        progressBar.style.width = percent + '%';
                        progressText.innerText = percent + '%';
                    }
                };
                
                xhr.onload = () => {
                    progressText.innerText = 'Upload Complete!';
                    setTimeout(() => {
                        progressContainer.classList.add('hidden');
                        dropText.innerText = 'Tap to select files';
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
                    li.innerHTML = `
                        <span>${filename}</span>
                        <a href="/download/${filename}" class="bg-white/20 px-3 py-1 rounded-lg text-xs hover:bg-white/30">Download</a>
                    `;
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
        contents = await file.read()
        with open(UPLOAD_DIR / file.filename, "wb") as f:
            f.write(contents)
        print(f"DEBUG: Ricevuto [{file.filename}]")
    return {"status": "success"}

@app.get("/files")
async def list_files():
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    return files

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

if __name__ == "__main__":
    ip = get_ip_address()
    url = f"http://{ip}:8000"
    print(f"\nServer running at {url}\n")
    print("QR Code:")
    qr = segno.make(url)
    qr.terminal(border=1, compact=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
