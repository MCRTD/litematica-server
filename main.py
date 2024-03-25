from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from t3dlitematica import LitimaticaToObj, Resolve, convert_texturepack
import os

app = FastAPI()


def check():
    if not os.path.exists("textures"):
        os.mkdir("textures")
    if not os.path.exists("obj"):
        os.mkdir("obj")
    if not os.path.exists("temp"):
        os.mkdir("temp")


@app.get("/")
def read_root():
    return {"message": "Litematica API is online"}


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.post("/litematica/upload")
def upload_litematica(file: UploadFile, texturepack: str) -> File:
    if not file.filename.endswith(".litematica"):
        return {"error": "File must be a .litematica file"}
    with open(os.path.join("temp", file.filename), "wb") as f:
        f.write(file.file.read())
    filename = LitimaticaToObj(
        Resolve(os.path.join("temp", file.filename)),
        os.path.join("textures", texturepack),
        "/obj",
    )
    return FileResponse(path=os.path.join("obj", filename), filename=filename)


@app.post("/litematica/resolve")
def resolve_litematica(file: UploadFile):
    if not file.filename.endswith(".litematica"):
        return {"error": "File must be a .litematica file"}
    with open(os.path.join("temp", file.filename), "wb") as f:
        f.write(file.file.read())
    return Resolve(os.path.join("temp", file.filename))


@app.post("/texturepack/upload")
def upload_texturepack(file: UploadFile):
    if not file.filename.endswith(".zip"):
        return {"error": "File must be a .zip file"}
    with open(os.path.join("temp", file.filename), "wb") as f:
        f.write(file.file.read())
    convert_texturepack(os.path.join("temp", file.filename), "/textures")
    return {"message": "Upload Texturepack"}


@app.get("/texturepack/list")
def list_texturepack():
    texturepacklist = os.listdir("textures")
    if not texturepacklist:
        return {"error": "No texturepack found"}
    return {"texturepacks": texturepacklist}


check()
