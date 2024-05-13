from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores.chroma import Chroma
from dataclasses import asdict
import os
import json
from langchain.tools import tool
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings
import requests
from bs4 import BeautifulSoup
from langchain_community.docstore.document import Document
from _temp.config import ChromaClient
from dataclasses import dataclass,asdict
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings

from _temp.config import OpenAIConfig, ChromaClient,PERSISTANT_DRIVE

'''
__import__('pysqlite3')
import sys
sys.modules['sqlite3']= sys.modules.pop('pysqlite3')
'''
import chromadb
from chromadb.config import Settings
import re
import html2text


class Embeddings:
    def __init__(self,name) -> None:
        self.name=name
    def load(self):
        return HuggingFaceEmbeddings(model_name=self.name)
    
class ConvertURLtoVector:    
    def __init__(self,embeddings) -> None:
        self.embeddings=Embeddings(embeddings).load()
        self.client = chromadb.HttpClient(**asdict(ChromaClient()),settings=Settings(allow_reset=True, anonymized_telemetry=False))

    def convert_url_to_vector(self, url_path, store_name):
        try:
            response = requests.get(url_path)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            excluded_tagNames = ["header", 'footer', 'nav']
            for tag_name in excluded_tagNames:
                for unwanted_tag in soup.find_all(tag_name):
                    unwanted_tag.extract()        

            url_content = html2text.html2text(str(soup))

            # Remove all links
            link_pattern = re.compile(r'https?://\S+')            
            url_content = re.sub(link_pattern, '', url_content)
            print(url_content)
        
            text_splitter = SemanticChunker(self.embeddings)
            doc = text_splitter.create_documents([url_content])
            print(doc)
            vdb=Chroma(embedding_function=self.embeddings,persist_directory=PERSISTANT_DRIVE,client=self.client,collection_name=store_name)
            vdb=vdb.from_documents(doc,embedding=self.embeddings,persist_directory=PERSISTANT_DRIVE,collection_name=store_name,client=self.client)    
            vdb.persist()

        except requests.exceptions.RequestException as e:
            url_content = None
            print(f"Error fetching data from {url_path}: {e}")
