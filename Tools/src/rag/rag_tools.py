from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain_openai.chat_models import AzureChatOpenAI

#local Imports
from Tools.src import tool_utils
from Tools.schema.rag_schema import MergeTool,KGTool,RagTool
from Tools.src.rag import rag_utils

API_KEY="312ff50d6d954023b8748232617327b6"

# --------------TBD -----------------------
def llmbuilder(name):
    if name =="azureopenai":
        return AzureChatOpenAI(api_key=API_KEY,
                    azure_endpoint="https://openai-lh.openai.azure.com/",
                    openai_api_version="2024-02-15-preview",
                    azure_deployment="test",
                    #azure_deployment="gpt-35-turbo-0613",
                    temperature=0
                   )
    else:
        return None
    
    
def chatmodel(qs,context,llm):
    RAG_TEMPLATE=PromptTemplate.from_template('''Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Use three sentences maximum and keep the answer as concise as possible.
        Always say "thanks for asking!" at the end of the answer.

        {context}

        Question: {question}

        Helpful Answer:''')
    rag_chain=RAG_TEMPLATE |llm
    #context=make_context(docs)
    out=rag_chain.invoke({"question":qs,"context":context})
    return out

# --------------TBD -----------------------


@tool(return_direct=False,args_schema=RagTool)
def rag(query:str,storage_name:str)->list:
    """Returns results from searching documents in vector database"""
    #embeddings=rag_utils.load_embeddings()
    #db=rag_utils.load_vectordb(storage_name,embeddings)
    
    #documents=db.invoke(query)
    #return rag_utils.make_context(documents)
    return "Search VectorDB"
    

@tool(return_direct=True,args_schema=KGTool)
def kg_rag(query:str)->list:
    """Returns results from searching documents in Knowledge Graph"""
    return "Knowledge Graph"

@tool(args_schema=MergeTool)
def mergetool(query:str,llm:str=None,prev_tools=None,intermediatory_steps=None)->str:
    """Merge the output of other tools and gives response to the user."""
    #print(query,llm,prev_tools,intermediatory_steps)
    '''
    is_func=tool_utils.check_if_func_call_required(llm)
    if is_func:
        llm_func=eval(is_func)
    merged_context="" 
    for i in prev_tools:
        merged_context+=intermediatory_steps[i]
    out=chatmodel(query,merged_context,llm_func)
    return out.content
    '''
    return "Responce"