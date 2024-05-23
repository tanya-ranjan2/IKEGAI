from langchain.tools import BaseTool, StructuredTool, Tool, tool
from Tools.schema.advanced_rag_schema import AdvanceRag
from Tools.src.advanced_rag.advanced_rag_utils import CompartiveAnalysisAdvancedRag
from _temp.config import UseCaseMongo
from DataIngestion.utils import mongo_utils
import tiktoken



@tool(return_direct = True, args_schema=AdvanceRag) 
def advanced_rag(user_query:str, **kwargs) -> str :
    """
    Returns results from searching multiple documents in vector database
    """
    agent_state = kwargs['state']  

    # retrieve meta data  
    meta_data = agent_state.config['data_sources']['meta_data']
    
    obj = CompartiveAnalysisAdvancedRag(meta_data)
    result = obj.predict(user_query)

    #agent_state.state["competitive_analysis_result"] = result
    agent_state.state['sources']=result['info_list']
    agent_state.state["context"]=result["context"]
    #print("Results:",result)
    context=result["context"]
    encoding = tiktoken.get_encoding("cl100k_base")
    encodded_data=encoding.encode(context)
    print("-------------->NUM TOKENS:",len(context.split()),len(encodded_data))
    print(context)
    return result["context"][:50000]