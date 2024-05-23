from langchain_openai.chat_models import AzureChatOpenAI
from dataclasses import dataclass,asdict
import chromadb
from chromadb.config import Settings
from langchain.memory import ChatMessageHistory



from _temp.config import OpenAIConfig, ChromaClient, EMBEDDING
from Tools.src.advanced_rag.utils.advanced_rag import advanced_retrival
from Tools.src.advanced_rag.utils.prompt_utils import get_rag

from langchain_community.embeddings import HuggingFaceEmbeddings
import tiktoken

class Embeddings:
    def __init__(self,name) -> None:
        self.name=name
    def load(self):
        return HuggingFaceEmbeddings(model_name=self.name)

class CompartiveAnalysisAdvancedRag:
    def __init__(self, meta_store) -> None:
        self.llm=AzureChatOpenAI(**asdict(OpenAIConfig()))
        self.embeddings=Embeddings(EMBEDDING).load()
        self.client= chromadb.HttpClient(**asdict(ChromaClient()))
        self.rag_chain=get_rag(self.llm)
        #self.chat_history=ChatMessageHistory()
        ## ? CODE- Fetch Metastore from mongoDB, usecase collection  
        self.meta_store = meta_store
    def convert_to_string(self,history,n=2):
        text=""
        for m in history.dict()['messages'][-n:]:
            text+=f"{m['type']} : {m['content']}\n"
        return text
    
    def predict(self,query):
        #prev_conv=self.convert_to_string(self.chat_history)
        data=advanced_retrival(self.llm,self.meta_store,query=query,embeddings=self.embeddings,chroma_client=self.client)
        
        info_list=[d.metadata for d in data]
        chunks={}
        for info in data:
            file_name=info.metadata['path']
            if file_name in chunks:
                chunks[file_name].append(info.page_content)
            else:
                chunks[file_name]=[info.page_content]
        context="\n\n".join([d.page_content for d in data])
        #print("advanced retrieval data --> ", context)
        #chunks_of_rag=[]
        #for c in chunks:
        #    context="\n".join(chunks[c])
        #    out=self.rag_chain.invoke({
        #        "context":f"# Content from document {c}  \n {context}",
        #        "user_query":query,
        #    })
        #    chunks_of_rag.append(out.content)
        #self.chat_history.add_user_message(query)
        #self.chat_history.add_ai_message(out.content)
        #Same code
        
        #info_list=[d.metadata for d in data]
        unique = dict()
        for item in info_list:
            # concatenate key
            key = f"{item['path']}{item['page']}"
            # only add the value to the dictionary if we do not already have an item with this key
            if not key in unique:
                unique[key] = item
        info_list=list(unique.values())
        info_list=[{"page":m['page'],"path":m["path"].split("/")[-1]} for m in info_list]
        return {
            #"context":"\n\n".join(chunks_of_rag),
            "context":context,
            "documents":data,
            "info_list":info_list
        }
        #return {
        #    "context":context,
        #    "documents":data,
        #    "info_list":info_list
        #    "output":out.content
        #}