from langchain.prompts import PromptTemplate
from langchain.tools import tool
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain_openai.chat_models import AzureChatOpenAI
 
#local Imports
from Tools.schema.scrapper_schema import ScrapperTool
from Tools.src.url_scrapper import scrapper_utils
 
 
@tool(return_direct=True, args_schema=ScrapperTool)
def scrapper(query: str, url:str, **kwargs)->str:
    """Returns answer based on the content retrieved from url and `user query`"""
    agent_state=kwargs['state']
    data_sourse=agent_state.config['data_sources']
    embeddings = scrapper_utils.load_embeddings()
    db=scrapper_utils.load_vectordb(data_sourse['storage_name'],
                                    embeddings,
                                    topk=10,
                                    collection_name=data_sourse['collection_name']
                                    )
    result=db.invoke(query+", answer from url")
    agent_state.state["scrapper_result"] = result
    return str(result)
