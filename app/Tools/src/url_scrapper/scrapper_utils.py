from langchain.tools import tool
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import AzureOpenAIEmbeddings
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import CharacterTextSplitter
import html2text

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
        excluded_tags = excluded_tagNames or []
        for tag_name in excluded_tags:
            for unwanted_tag in soup.find_all(tag_name):
                unwanted_tag.extract()

        text_content = html2text.html2text(str(soup))
        # print(text_content)
        return text_content
    
    except requests.exceptions.RequestException as e:
        # print(f"Error fetching data from {url}: {e}")
        return f"Error fetching data from {url}: {e}"

def load_vectordb(text, embeddings):
    text_splitter = CharacterTextSplitter(
        separator = "\n",
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len
    )
    
    texts = text_splitter.split_text(text)
    db = Chroma.from_texts(texts, embeddings)
    # docs = db.similarity_search(query)
    qa = RetrievalQA.from_chain_type(llm=llm(),
                                     chain_type="stuff",
                                     retriever=db.as_retriever(),
                                    #  return_source_documents=True,
                                     verbose=True)
    return qa
