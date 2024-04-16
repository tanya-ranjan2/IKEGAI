# File Ingestion and Vector Database Storage

This repository contains a FastAPI application that allows users to upload files (PDF, TXT, DOCX, and SQLite databases) and stores their text content as embedding in a Chroma vector database.

The file processing is offloaded to a Celery task, which runs concurrently using multithreading.

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.12
- Redis (for Celery broker and backend) (VM)
- MongoDB (for storing task responses)
- Chroma vector database server (in VM)

- Create a conda/venv environment before running the code.

- Install the required Python packages:
```pip install -r requirements.txt```

In one command prompt terminal/ bash terminal (Linux/Ubuntu), first activate conda/venv environment 

- run the celery worker using:
```celery -A celery_chroma_ingest worker --loglevel=INFO --pool=solo```

Open another CMD terminal/ bash terminal, first activate conda/venv environment

- run the main.py (FastAPI script) using below:
``` python main.py```

## Usage
- Upload files by sending a POST request to http://localhost:8000/data_ingestion with the files in the request body.
- Check the status of file processing tasks by sending a GET request to http://localhost:8000/responses.
- The uploaded files will be processed by the Celery task, and their text content will be stored in the Chroma vector database.
  The task responses will be stored in the MongoDB database.

## Resources used:
- https://celery.school/celery-on-windows
- https://stackoverflow.com/questions/45744992/celery-raises-valueerror-not-enough-values-to-unpack
- https://docs.celeryq.dev/en/latest/reference/celery.result.html
- https://medium.com/@Aman-tech/celery-with-flask-d1f1c555ceb7
- https://celery.school/custom-celery-task-states
- https://celery.school/celery-on-windows



