import os
import datetime
from celery import Celery
from celery.schedules import crontab
import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain_core.documents.base import Document
import PyPDF2
from redis import Redis
import logging
from celery.result import AsyncResult
from langchain.text_splitter import RecursiveCharacterTextSplitter
import docx
from typing import List
import concurrent.futures
import time
import sqlite3

logger = logging.getLogger(__name__)

# Celery setup
redis = Redis(host="20.41.249.147", port=6379, username="default", password="admin", db=0)
app = Celery('celery_chroma_ingest', broker='redis://20.41.249.147:6379/0', backend="redis://20.41.249.147:6379/0")

# Initialize Chroma DB client
# chroma_client = chromadb.PersistentClient(path="chromadb")
chroma_client = chromadb.HttpClient(host="20.41.249.147", port=6062)

collection = chroma_client.get_or_create_collection(name="pdf_database")

# Initialize a set to store processed file paths
processed_files = set()

def get_text(file_path):
    if file_path.endswith('.pdf'):
        pdf_file = open(file_path, 'rb')
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
        pdf_file.close()
        text = text
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        text = ""
    return text

def get_text_from_database(file_path):
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'") # fetching list of tables from sqlite3 database
    tables = [row[0] for row in cursor.fetchall()]

    text = ""

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})") # fetching list of column names, data types

        # Fetch data from all columns
        rows = []
        for row in cursor.execute(f"SELECT * FROM {table}"):
            row_text = " ".join(str(value) for value in row)
            rows.append(row_text)

        text += "\n".join(rows) + "\n"

    conn.close()
    return text

# Initialize text splitter and embeddings
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
# embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")
embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-base-v2")

def create_file_embedding(file_path):
    try:
        # skipping already processed files
        if file_path in processed_files:
            logger.info(f"{os.path.basename(file_path)} has already been processed. Skipping.")
            return
        
        start_time = time.perf_counter()

        if file_path.endswith('.db'):
            # Get text from the database
            text = get_text_from_database(file_path)
        else:
            text = get_text(file_path)
        chunks = text_splitter.split_text(text)

        # Convert chunks to vector representations and store in Chroma DB
        documents_list = []
        embeddings_list = []
        ids_list = []
        for i, chunk in enumerate(chunks):
            vector = embeddings.embed_query(chunk)
            documents_list.append(chunk)
            embeddings_list.append(vector)
            ids_list.append(f"{os.path.basename(file_path)}_{i}")

        collection.add(embeddings=embeddings_list, documents=documents_list, ids=ids_list)
        logger.info(f"Stored {os.path.basename(file_path)} in vector database")
        processed_files.add(file_path)  # Add the processed file path to the set

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken to process {os.path.basename(file_path)}: {elapsed_time:.2f} seconds")
        
    except Exception as e:
        logger.warning(f"Error processing {os.path.basename(file_path)}: {e}")

@app.task
def process_files():
    uploads_dir = 'uploads'
    files_to_process = []
    for filename in os.listdir(uploads_dir):
        if filename.endswith('.pdf') or filename.endswith(".txt") or filename.endswith(".docx") or filename.endswith('.db'):
            file_path = os.path.join(uploads_dir, filename)
            files_to_process.append(file_path)

    # using threadpool for multithreading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(create_file_embedding, file_path) for file_path in files_to_process]

        # Wait for all tasks to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.warning(f"Error processing file: {e}")

    print("------")
    print(collection)
    task_id = process_files.request.id
    return task_id

# Register the task with the Celery app
app.tasks.register(process_files)

if __name__ == "__main__":
    app.start()