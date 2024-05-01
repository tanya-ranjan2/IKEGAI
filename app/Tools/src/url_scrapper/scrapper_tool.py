from langchain.prompts import PromptTemplate
from langchain.tools import tool
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_community.vectorstores import Chroma
 
#local Imports
from Tools.schema.scrapper_schema import ScrapperTool
from Tools.src.url_scrapper import scrapper_utils
 
 
@tool(return_direct=True, args_schema=ScrapperTool)
def scrapper(query: str, url:str, **kwargs)->str:
    """Returns answer based on the content retrieved from url and `user query`"""
    agent_state=kwargs['state']
    text = scrapper_utils.get_text_from_url(url)
    embeddings = scrapper_utils.load_embeddings()
    qa = scrapper_utils.load_vectordb(text, embeddings)
    result = qa.invoke({"query": query+"answer from url"})
    agent_state.state["scrapper_result"] = result
    return str(result)
