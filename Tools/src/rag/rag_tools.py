from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain_openai.chat_models import AzureChatOpenAI

#local Imports
from Tools.src import tool_utils
from Tools.schema.rag_schema import KGTool,RagTool
from Tools.src.rag import rag_utils
from utils.llmops import llmbuilder


# --------------TBD -----------------------

    
    
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
def rag(query:str,storage_name:str,**kwargs)->list:
    """Returns results from searching documents in vector database"""
    agent_state=kwargs['state']
    
    embeddings=rag_utils.load_embeddings()
    db=rag_utils.load_vectordb(storage_name,embeddings)
    
    documents=db.invoke(query)
    reference=[i.metadata for i in documents]
    print(reference)
    agent_state.state['rag']=reference
    return rag_utils.make_context(documents)
    #return "Search VectorDB"
    

@tool(return_direct=True,args_schema=KGTool)
def kg_rag(query:str)->list:
    """Returns results from searching documents in Knowledge Graph"""
    return "Knowledge Graph"

