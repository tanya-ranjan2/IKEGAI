from langchain.tools import tool
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.docstore.document import Document
from _temp.config import ChromaClient,EMBEDDING
from dataclasses import dataclass,asdict
from langchain_community.embeddings import HuggingFaceEmbeddings

import chromadb
from chromadb.config import Settings

'''
__import__('pysqlite3')
import sys
sys.modules['sqlite3']= sys.modules.pop('pysqlite3')
'''

def load_embeddings():
    embeddings=HuggingFaceEmbeddings(EMBEDDING)
    return embeddings
    
def load_vectordb(persist_directory,embeddings,topk=10,collection_name=None):

    client = chromadb.HttpClient(**asdict(ChromaClient()),settings=Settings(allow_reset=True, anonymized_telemetry=False))

    if collection_name==None or collection_name=="":
        db=Chroma(persist_directory=persist_directory,embedding_function=embeddings,client=client)
    else:
        db=Chroma(persist_directory=persist_directory,embedding_function=embeddings,client=client,collection_name=collection_name)

    search_kwargs = {
    "maximal_marginal_relevance": True,
    "distance_metric": "cos", 
    "k": topk
}
    retriver=db.as_retriever(
                            search_type="mmr",
                            #  search_type="similarity",
                            #  search_kwargs={"k": topk}
                             search_kwargs=search_kwargs
                             )
    return retriver
