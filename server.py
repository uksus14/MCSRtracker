#!/home/knight/personal-packages/friends/MCSR/env/bin/python
import os

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import FastAPI, Response
from persistent import persistent
from sheets_copy import make_copy
import subprocess

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def index():
    return FileResponse('static/index.html')

@app.get("/fetch")
def fetch():
    persistent.fetch()
    return Response()

@app.get("/html")
def html(start: int|None=None, end: int|None=None):
    return HTMLResponse(make_copy(persistent.runs[slice(start, end)]))

if __name__ == "__main__":
    import uvicorn
    port = 9999
    if os.name == 'unix':
        service_result = subprocess.run(['my-service', 'ensure', 'MCSR'], capture_output=True, text=True, check=True)
        port = int(service_result.stdout.strip())
    uvicorn.run('server:app', host='0.0.0.0', port=port)
    # uvicorn.run('server:app', host='0.0.0.0', port=9999)