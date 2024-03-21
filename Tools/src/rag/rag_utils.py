
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma



def load_embeddings():
    embeddings=HuggingFaceEmbeddings()
    return embeddings

def load_vectordb(persist_directory,embeddings,topk=2):
    db=Chroma(persist_directory=persist_directory,embedding_function=embeddings)
    retriver=db.as_retriever(search_type="similarity", search_kwargs={"k": topk})
    return retriver

def make_context(docs):
    context=""
    for a in docs:
        context+=a.page_content
    return context




