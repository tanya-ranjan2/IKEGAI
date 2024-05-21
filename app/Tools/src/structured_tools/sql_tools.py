from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain_openai.chat_models import AzureChatOpenAI

#local Imports
from Tools.src import tool_utils
from Tools.schema.structured_schema import SQLGeneratorTool,SQLExecutor
from Tools.src.structured_tools.sql_utils import PromptMaker
# from Tools.src.structured_tools.sql_utils import PromptMaker


@tool(return_direct=True,args_schema=SQLGeneratorTool)
def sql_generator(query:str,**kwargs)->list:
    """Generate the SQL query from natural language `user query`. Run sql_executor after this"""
    agent_state=kwargs['state']
    data_source=agent_state.config['data_sources']
    db_path = data_source["db_path"]
    def_path = data_source["db_def_path"]
    db_type = data_source["db_type"]
    query = agent_state.state["input"]
    print(100*"=")
    print(kwargs)
    print(f"{query=}, {agent_state=},{db_path=},{def_path=}" )
    resp =  PromptMaker(prompt_text=query,
            name="",
            db_uri=db_path,
            filepath=def_path,
            db_type=db_type).get_prompt_answer()

    answer = resp.get("answer", "No data") or "No data retrived"
    chart = resp.get("chart_config", []) or []
    data = resp.get("tabular_answer", "No data") or "No data retrived"
    table = resp.get("raw_table", []) or []

    print(resp)
    print(10*"*")
    
    agent_state.state['sources']=[]
    agent_state.state['chart_config']=chart
    agent_state.state['data']=data
    agent_state.state["table"] = table
    return answer
   


@tool(return_direct=False,args_schema=SQLExecutor)
def sql_executor(sql_query:str,creds:dict={})->list:
    """Executes the generated SQL query and returns the data. Once the `sql_generator` is called. This function must be called """
    print(creds)
    return "SQL Query Executed"