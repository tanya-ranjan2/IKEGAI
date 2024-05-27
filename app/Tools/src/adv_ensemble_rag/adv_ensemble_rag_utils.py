from pymongo import MongoClient
from dataclasses import dataclass,asdict
from langchain_openai.chat_models import AzureChatOpenAI
from langchain.prompts import PromptTemplate
import json
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
import tiktoken
from langchain_core.documents import Document
import tqdm
import numpy as np

from Tools.utils import model_helper
from _temp.config import ChromaClient,MAX_TOKEN_CONTEXT_LIMIT



def make_documents_from_chroma(document_chunks):
    return [Document(page_content=d,metadata=m or {}) for d,m in zip(document_chunks['documents'],document_chunks['metadatas'])]

def ensemble_retriver(query,collections,client,embeddings):
    documents=[]
    for collection in tqdm.tqdm(collections):
        vdb=Chroma(client=client,collection_name=collection,embedding_function=embeddings)
        document_chunks=vdb.get()
        bm_docs=make_documents_from_chroma(document_chunks)
        bm25_retriver=BM25Retriever.from_documents(bm_docs)
        retriver=vdb.as_retriever()
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriver, retriver], weights=[0.5, 0.5]
        )
        retrived_docs=ensemble_retriever.invoke(query)
        documents.extend(retrived_docs)
    return documents

def rerank_docs(query,documents,reranker):
    fscores_n=[]
    for d in tqdm.tqdm(documents):
        #print(d.page_content)
        score = reranker.compute_score([query, d.page_content])
        fscores_n.append(score)
    return fscores_n

def get_final_documents(sorted_idx,scores,documents,max_token_limit):
    encoding = tiktoken.get_encoding("cl100k_base")
    final_docs=[]
    context_limit=0
    for d_index in sorted_idx:
        doc=documents[d_index]
        if scores[d_index]>0 and context_limit<max_token_limit:
            encoded=encoding.encode(doc.page_content)
            context_limit+=len(encoded)
            final_docs.append(doc)
        else:
            break
    return final_docs
        
def advance_retrival(query,data_sources):
    
    
    if 'meta_data' not in data_sources:
        raise Exception("'meta_data' feild missing in data sources")
    client = chromadb.HttpClient(**asdict(ChromaClient()))
    collections=[c['collection_name'] for c in data_sources['meta_data']]
    embeddings=model_helper.load_embeddings()
    reranker=model_helper.load_reranker()
    
    retrived_documents=ensemble_retriver(query,collections,client,embeddings)
    document_score=rerank_docs(query,retrived_documents,reranker)
    
    sorted_arg_idx=list(np.argsort(document_score))[::-1]
    final_docs=get_final_documents(sorted_arg_idx,document_score,retrived_documents,MAX_TOKEN_CONTEXT_LIMIT)
    context="\n\n".join([i.page_content for i in final_docs])
    info_list=model_helper.get_document_source(final_docs)
    return {
        "context": context,
        "info_list":info_list
    }
