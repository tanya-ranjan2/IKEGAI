from langchain.tools import tool
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import MarkdownTextSplitter
# from langchain_core.documents.base import Document
# from langchain_core.documents import Document
from langchain_community.docstore.document import Document
# from langchain_community.vectorstores import Chroma
from _temp.config import ChromaClient
from dataclasses import dataclass,asdict
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings

import chromadb
from chromadb.config import Settings
import re

'''
__import__('pysqlite3')
import sys
sys.modules['sqlite3']= sys.modules.pop('pysqlite3')
'''

def load_embeddings():
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint='https://openai-lh.openai.azure.com/',
        openai_api_key='312ff50d6d954023b8748232617327b6',
        deployment='LH-embedding',
        openai_api_version='2023-06-01-preview',
        openai_api_type="azure"
    )
    return embeddings

def llm():
    llm = AzureChatOpenAI(
        openai_api_base="https://openai-lh.openai.azure.com/openai/deployments/LH-GPT",
        openai_api_version='2023-06-01-preview',
        openai_api_key='312ff50d6d954023b8748232617327b6',
        temperature=0, max_tokens=4096, verbose=True
    )
    return llm

def get_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        excluded_tagNames = ["header", 'footer', 'nav']
        for tag_name in excluded_tagNames:
            for unwanted_tag in soup.find_all(tag_name):
                unwanted_tag.extract()        

        text_content = html2text.html2text(str(soup))

        # Remove all links
        link_pattern = re.compile(r'https?://\S+')
        text_content = re.sub(link_pattern, '', text_content)

        print(text_content)
        return text_content
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching data from {url}: {e}"
    
def load_vectordb(text, persist_directory,embeddings,topk=10,collection_name=None):

    text_splitter = SemanticChunker(load_embeddings())
    doc = text_splitter.create_documents([text])

    client = chromadb.HttpClient(**asdict(ChromaClient()),settings=Settings(allow_reset=True, anonymized_telemetry=False))

    if collection_name==None or collection_name=="":
        db=Chroma.from_documents(doc,persist_directory=persist_directory,embedding=embeddings,client=client)
    else:
        db=Chroma.from_documents(doc,persist_directory=persist_directory,embedding=embeddings,client=client,collection_name=collection_name)

    retriver=db.as_retriever(search_type="similarity",
                             search_kwargs={"k": topk}
                             )
    return retriver
