#!/home/knight/personal-packages/friends/MCSR/env/bin/python
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from persistent import persistent
from sheets_copy import make_copy
from dataclasses import asdict
from fastapi import FastAPI
import subprocess
import webbrowser
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def index():
    return FileResponse('static/index.html')

@app.get("/fetch")
def fetch(): return [asdict(run) for run in persistent.fetch()]

@app.get("/html")
def html(start: int|None=None, end: int|None=None):
    return HTMLResponse(make_copy(persistent.runs[slice(start, end)]))

#TODO endfight, discard, discarded

if __name__ == "__main__":
    import uvicorn
    port = 9999
    if os.name == 'posix':
        service_result = subprocess.run(['my-service', 'ensure', 'MCSR'], capture_output=True, text=True, check=True)
        port = int(service_result.stdout.strip())
    webbrowser.open(f"127.0.0.1:{port}")
    uvicorn.run('server:app', host='0.0.0.0', port=port)