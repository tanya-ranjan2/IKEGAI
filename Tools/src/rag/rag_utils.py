
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from _temp.config import ChromaClient
from dataclasses import dataclass,asdict

__import__('pysqlite3')
import sys
sys.modules['sqlite3']= sys.modules.pop('pysqlite3')

import chromadb
from chromadb.config import Settings


def load_embeddings():
    embeddings=HuggingFaceEmbeddings(model_name="intfloat/e5-base-v2")
    return embeddings

def load_vectordb(persist_directory,embeddings,topk=2,collection_name=None):
    client = chromadb.HttpClient(**asdict(ChromaClient()))
    if collection_name==None or collection_name=="":
        db=Chroma(persist_directory=persist_directory,embedding_function=embeddings,client=client)
    else:
        db=Chroma(persist_directory=persist_directory,embedding_function=embeddings,client=client,collection_name=collection_name)
    retriver=db.as_retriever(search_type="similarity", search_kwargs={"k": topk})
    return retriver

def make_context(docs):
    context=""
    for a in docs:
        context+=a.page_content
    return context




