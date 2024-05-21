from langchain.tools import BaseTool, StructuredTool, Tool, tool
from Tools.schema.advanced_rag_schema import AdvanceRag
from Tools.src.advanced_rag.advanced_rag_utils import CompartiveAnalysisAdvancedRag
from _temp.config import UseCaseMongo
from DataIngestion.utils import mongo_utils


@tool(return_direct = True, args_schema=AdvanceRag) 
def advanced_rag(user_query:str, **kwargs) -> str :
    """
    Generate a competitive analysis of two documents based on the user query
    """
    agent_state = kwargs['state']  

    # retrieve meta data  
    meta_data = agent_state.config['data_sources']['meta_data']
    
    obj = CompartiveAnalysisAdvancedRag(meta_data)
    result = obj.predict(user_query)

    agent_state.state["competitive_analysis_result"] = result
    return result["output"]