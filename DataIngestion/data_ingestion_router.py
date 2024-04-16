from fastapi import APIRouter
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import FileResponse
import os

from celery_queue import uploadpdf

from _temp.config import STORAGE_DRIVE


router=APIRouter(prefix='/ingestion',tags=["data_ingestion"])

if not os.path.exists(STORAGE_DRIVE):
    os.mkdir(STORAGE_DRIVE)


@router.post("/uploadfile/{idx}")
async def create_upload_file(file: UploadFile,idx:str):
    
    contents = file.file.read()
    with open(os.path.join(STORAGE_DRIVE,file.filename), 'wb') as f:
        f.write(contents)
    uploadpdf.delay(idx,os.path.join(STORAGE_DRIVE,file.filename))
    return {"filename": file.filename}


@router.get("/download/{filename}")
async def dowload(filename:str):
    pdf_name_mapping={'az1742-2018.pdf':'Solar Photovoltic (PV) System Components.pdf',
                          '6981.pdf':"Photovoltics: Basic Design Princicals and Components.pdf",
                          'BOOK3.pdf':"Solar Photovoltics Technology and Systems.pdf"
                          }
    reverse_mapping={v:k for k,v in pdf_name_mapping.items()}
    if filename in reverse_mapping:
        filename=reverse_mapping[filename]
    file_path=os.path.join(STORAGE_DRIVE,filename)
    return FileResponse(path=file_path, filename=file_path, media_type='text/pdf')