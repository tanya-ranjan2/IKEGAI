from langchain_community.embeddings import HuggingFaceEmbeddings
from FlagEmbedding import FlagReranker

from _temp.config import EMBEDDING,RERANKER_MODEL


def load_embeddings():
    embeddings=HuggingFaceEmbeddings(model_name=EMBEDDING)
    return embeddings

def load_reranker():
    return FlagReranker(RERANKER_MODEL) # Setting use_fp16 to True speeds up computation with a slight performance degradation

def get_document_source(docs):
    info_list=[d.metadata for d in docs]
    unique = dict()
    for item in info_list:
        # concatenate key
        key = f"{item['path']}{item['page']}"
        # only add the value to the dictionary if we do not already have an item with this key
        if not key in unique:
            unique[key] = item
    info_list=list(unique.values())
    info_list=[{"page":m['page'],"path":m["path"].split("/")[-1]} for m in info_list]
    return info_list