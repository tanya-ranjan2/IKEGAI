from fastapi import APIRouter
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import FileResponse
import os

from celery_queue import uploadpdf

from _temp.config import STORAGE_DRIVE


router=APIRouter(prefix='/ingestion',tags=["data_ingestion"])

router.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists(STORAGE_DRIVE):
    os.mkdir(STORAGE_DRIVE)


@router.post("/uploadfile/{idx}")
async def create_upload_file(file: UploadFile,idx:str):
    
    contents = file.file.read()
    with open(os.path.join(STORAGE_DRIVE,file.filename), 'wb') as f:
        f.write(contents)
    uploadpdf.delay(idx,os.path.join(STORAGE_DRIVE,file.filename))
    return {"filename": file.filename}