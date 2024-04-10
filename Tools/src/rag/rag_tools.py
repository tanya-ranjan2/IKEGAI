from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain_openai.chat_models import AzureChatOpenAI

#local Imports
from Tools.src import tool_utils
from Tools.schema.rag_schema import KGTool,RagTool
from Tools.src.rag import rag_utils
from utils.llmops import llmbuilder




@tool(return_direct=False,args_schema=RagTool)
def rag(query:str,**kwargs)->list:
    """Returns results from searching documents in vector database"""
    agent_state=kwargs['state']
    data_sourse=agent_state.config['data_sources']
    embeddings=rag_utils.load_embeddings()
    db=rag_utils.load_vectordb(data_sourse['storage_name'],embeddings)
    
    documents=db.invoke(query)
    reference=[i.metadata for i in documents]
    agent_state.state['sources']=reference
    return rag_utils.make_context(documents)
    #return "Search VectorDB"
    

@tool(return_direct=True,args_schema=KGTool)
def kg_rag(query:str)->list:
    """Returns results from searching documents in Knowledge Graph"""
    return "Knowledge Graph"

