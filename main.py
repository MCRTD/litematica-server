from fastapi import FastAPI, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Union, List
from t3dlitematica import LitimaticaToObj, Resolve, convert_texturepack, multiload
import os
import re
import requests

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def check():
    if not os.path.exists("textures"):
        os.mkdir("textures")
    if not os.path.exists("obj"):
        os.mkdir("obj")
    if not os.path.exists("temp"):
        os.mkdir("temp")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def read_root():
    html = open("./public/index.html", "r").read()
    return html


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.post("/litematica/upload")
def upload_litematica(file: UploadFile | str, texturepack: Union[str, List[str]]) -> Response:
    if isinstance(file, str):
        try:
            match = re.match(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)\/([\w\-\.%]+\.litematic)\??.*", file)
            if not match:
                return {"error": "Invalid URL"}
            infilename = match.group(3)
            r = requests.get(file, stream=True)
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            return {"error": "Invalid URL"}
        with open(os.path.join("temp", infilename), "wb") as f:
            f.write(r.content)
    else:
        if not file.filename.endswith(".litematic"):
            return {"error": "File must be a .litematic file"}
        infilename = file.filename
        with open(os.path.join("temp", infilename), "wb") as f:
            f.write(file.file.read())
    if isinstance(texturepack, list):
        for tp in texturepack:
            if not os.path.exists(os.path.join("textures", tp)):
                raise HTTPException(
                    status_code=500, detail=f"{tp} Texturepack not found"
                )
        with multiload(texturepack) as texturepath:
            filename = LitimaticaToObj(
                Resolve(os.path.join("temp", infilename)),
                texturepath,
                os.path.join(os.getcwd(), "obj"),
            )
    else:
        print(Resolve(os.path.join("temp", infilename)))
        texturepath = os.path.join("textures", texturepack)
        filename = LitimaticaToObj(
            Resolve(os.path.join("temp", infilename)),
            texturepath,
            os.path.join(os.getcwd(), "obj"),
        )
    os.remove(os.path.join("temp", infilename))
    return FileResponse(path=os.path.join("obj", str(filename)), filename=str(filename))


@app.post("/litematica/resolve")
def resolve_litematica(file: UploadFile | str):
    if isinstance(file, str):
        try:
            match = re.match(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)\/([\w\-\.%]+\.litematic)\??.*", file)
            if not match:
                return {"error": "Invalid URL"}
            infilename = match.group(3)
            r = requests.get(file, stream=True)
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            return {"error": "Invalid URL"}
        with open(os.path.join("temp", infilename), "wb") as f:
            f.write(r.content)
    else:
        if not file.filename.endswith(".litematic"):
            return {"error": "File must be a .litematic file"}
        infilename = file.filename
        with open(os.path.join("temp", infilename), "wb") as f:
            f.write(file.file.read())
    data = Resolve(os.path.join("temp", infilename))
    os.remove(os.path.join("temp", infilename))
    return data



@app.post("/texturepack/upload")
def upload_texturepack(file: UploadFile, texturepackname: str):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=500, detail="File must be a .zip file")
    if os.path.exists(os.path.join("textures", texturepackname)):
        raise HTTPException(status_code=500, detail="Texturepack already exists")
    with open(os.path.join(os.getcwd(), "temp", file.filename), "wb") as f:
        f.write(file.file.read())
    os.mkdir(os.path.join("textures", texturepackname))
    convert_texturepack(
        os.path.join("temp", file.filename), os.path.join("textures", texturepackname)
    )
    os.remove(os.path.join("temp", file.filename))
    return {"message": "Upload Texturepack"}


@app.get("/texturepack/list")
def list_texturepack():
    texturepacklist = os.listdir("textures")
    if not texturepacklist:
        raise HTTPException(status_code=500, detail="No texturepacks found")
    return {"texturepacks": texturepacklist}


if __name__ == "__main__":
    import uvicorn
    check()
    uvicorn.run(app, host="127.0.0.1", port=8000)
