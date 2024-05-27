from langchain.tools import BaseTool, StructuredTool, Tool, tool
from Tools.schema.adv_ensemble_rag_schema import AdvanceRagEnsemble
from Tools.src.adv_ensemble_rag.adv_ensemble_rag_utils import advance_retrival
import tiktoken



@tool(return_direct = True, args_schema=AdvanceRagEnsemble) 
def advanced_rag_ensemble(user_query:str, **kwargs) -> str :
    """
    Returns results from searching multiple documents in vector database
    """
    agent_state = kwargs['state']  

    # retrieve meta data  
    meta_data = agent_state.config['data_sources']
    result=advance_retrival(user_query,meta_data)
    
    agent_state.state['sources']=result['info_list']
    agent_state.state["context"]=result["context"]
    print("Results:",result)
    context=result["context"]
    return context