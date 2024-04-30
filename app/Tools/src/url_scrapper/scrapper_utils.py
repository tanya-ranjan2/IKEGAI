from langchain.tools import tool
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import AzureOpenAIEmbeddings
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import TokenTextSplitter
from collections import deque
from bs4 import Tag, NavigableString
import pandas as pd
 
 
def load_embeddings():
    # embeddings=HuggingFaceEmbeddings()
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint = 'https://openai-lh.openai.azure.com/',
        openai_api_key = '312ff50d6d954023b8748232617327b6',  
        deployment = 'LH-embedding',
        openai_api_version = '2023-06-01-preview',
        openai_api_type = "azure"
    )
    return embeddings
 
def llm():
    llm = AzureChatOpenAI(
            openai_api_base = "https://openai-lh.openai.azure.com/openai/deployments/LH-GPT",
            openai_api_version = '2023-06-01-preview',
            openai_api_key = '312ff50d6d954023b8748232617327b6',
            temperature = 0, max_tokens = 4096, verbose = True
        )
    return llm

def extract_text(node):
    text = []
    stack = deque([node])
    formatting_functions = {
        'h1': lambda strings: f"\n# {''.join(s.strip() for s in strings)}",
        'h2': lambda strings: f"\n## {''.join(s.strip() for s in strings)}",
        'h3': lambda strings: f"\n### {''.join(s.strip() for s in strings)}",
        'h4': lambda strings: f"\n#### {''.join(s.strip() for s in strings)}",
        'h5': lambda strings: f"\n##### {''.join(s.strip() for s in strings)}",
        'h6': lambda strings: f"\n###### {''.join(s.strip() for s in strings)}",
        'p': lambda strings: f"\n{''.join(s.strip() for s in strings)}",
        'span': lambda strings: f"\`{''.join(s.strip() for s in strings)}\`",
        'li': lambda strings: f"\n- {''.join(s.strip() for s in strings)}",
        'strong': lambda strings: f"\n**{''.join(s.strip() for s in strings)}**"
    }

    while stack:
        current_node = stack.pop()
        if isinstance(current_node, NavigableString):
            # skipping navigablestring instances
            continue

        elif isinstance(current_node, Tag):
            # to skip javascript code and navbar element
            navbar_elements = ['nav', 'header', 'footer']
            if current_node.name == 'script' or current_node.name in navbar_elements:
                continue
            
            elif current_node.name in formatting_functions:
                    text.append(formatting_functions[current_node.name](current_node.strings))
            
            elif current_node.name == 'table':
                text.append(str(current_node))

            else:
                # For other non-heading or non-paragraph tags, extend the stack with their children
                children = reversed(list(current_node.children))
                stack.extend(children)                
    # print('\n'.join(text))
    return '\n'.join(text)

def get_text_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            content = extract_text(soup.body)
            return content
        else:
            return "failed to fetch content of url"
    except requests.exceptions.RequestException as e:
        return "error"
 
def load_vectordb(text, embeddings):
    text_splitter = CharacterTextSplitter(
        separator = "\n",
        chunk_size = 1000,
        chunk_overlap  = 100,
        length_function = len
    ) 
    texts = text_splitter.split_text(text)
    db = Chroma.from_texts(texts, embeddings)
    qa = RetrievalQA.from_chain_type(llm=llm(),
                                    chain_type="stuff",
                                    retriever=db.as_retriever())
    return qa
