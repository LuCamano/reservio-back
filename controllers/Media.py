from fastapi import UploadFile, File
import shutil
import os

MEDIA_DIR = "media"
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)
    
def upload_image(folder: str, file: UploadFile = File(...)):
    folder_path = os.path.join(MEDIA_DIR, folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_location = os.path.join(folder_path, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "folder": folder}