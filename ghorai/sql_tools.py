from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain_openai.chat_models import AzureChatOpenAI

#local Imports
from Tools.src import tool_utils
from Tools.schema.text_to_sql_schema import TextToSQL
from Tools.src.text_to_sql.sql_utils import execute_sql_query
from utils.llmops import llmbuilder
import pandas as pd

@tool(return_direct = False, args_schema=TextToSQL)
def text_to_sql(user_query, **kwargs) -> str :
    """
    this is the text_to_sql tool which executes an SQL query based on the given user_query. This takes input from `extract_keywords`
    """

    print('inside text_to_sql tool --> ', feature_parameters)
    agent_state = kwargs['state'] 
    feature_parameters = agent_state.state['feature_parameters']

    print(feature_parameters)
    result = execute_sql_query(feature_parameters)
    agent_state.state['filter_data'] = eval(result)
    return result
