from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain_openai.chat_models import AzureChatOpenAI

#local Imports
from Tools.src import tool_utils
from Tools.schema.rag_schema import KGTool,RagTool
from Tools.src.rag import rag_utils
from utils.llmops import llmbuilder
from Tools.utils import model_helper




@tool(return_direct=False,args_schema=RagTool)
def rag(query:str,topk:int=3,**kwargs)->list:
    """Returns results from searching documents in vector database"""
    agent_state=kwargs['state']
    data_sourse=agent_state.config['data_sources']
    embeddings=model_helper.load_embeddings()
    all_docs=[]
    all_refs=[]
    for d in data_sourse["vectorDB"]:
        db=rag_utils.load_vectordb(d['storage_name'],embeddings,collection_name=d['collection_name'],topk=topk)
    
        documents=db.invoke(query)
        
        cc_context=[i.page_content for i in documents]
        reference=[i.metadata for i in documents]
        info_list=[{"page":m['page'],"path":m["path"].split("/")[-1]} for m in reference]
        all_docs.extend(cc_context)
        all_refs.extend(info_list)

    agent_state.state['sources']=all_refs
    agent_state.state['context']= all_docs
    context="\n\n".join(all_docs)
    return context
    #return "Search VectorDB"
    

@tool(return_direct=True,args_schema=KGTool)
def kg_rag(query:str)->list:
    """Returns results from searching documents in Knowledge Graph"""
    return "Knowledge Graph"

