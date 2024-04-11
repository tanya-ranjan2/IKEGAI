from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain_openai.chat_models import AzureChatOpenAI

#local Imports
from Tools.src import tool_utils
from Tools.schema.extractor_schema import ExtractKeywords
from Tools.src.extractor.extractor_utils import extract_date_keywords, extract_feature_keywords
from Tools.src.text_to_sql.sql_utils import execute_sql_query 
from utils.llmops import llmbuilder
import pandas as pd

@tool(return_direct = True, args_schema=ExtractKeywords)
def extract_keywords(
        user_query: str, default_days: int = 5, **kwargs
    ) -> str: 
    """
    Extracts the univariate and multivariate features along with the date informations. Based on the extracted information creates and executes a sql query and gererate a filter_data which is passed inside the `forecast_using_prophet` tool.
    """
    print("input to the function --> ", user_query)
    agent_state = kwargs['state'] 
    extracted_feature = extract_feature_keywords(user_query = user_query) 
    extracted_date = extract_date_keywords(user_query = user_query, default_days = default_days)

    final_result = {**extracted_feature, **extracted_date}

    print(final_result)

    agent_state.state['feature_parameters'] = final_result
    filter_data = execute_sql_query(final_result)
    agent_state.state['filter_data'] = filter_data

    return filter_data
