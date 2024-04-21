from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain_openai.chat_models import AzureChatOpenAI

#local Imports
from Tools.src import tool_utils
from Tools.schema.forecasting_schema import ForecastingUsingProphet
from Tools.src.forecasting.forecasting_utils import forecast_using_prophet_utils
from Tools.src.extractor.extractor_utils import extract_feature_keywords_for_sql_query, extract_date_keywords
from Tools.src.text_to_sql.sql_utils import execute_sql_query
from utils.llmops import llmbuilder
import pandas as pd
 
@tool(return_direct = False, args_schema=ForecastingUsingProphet)
def forecast_using_prophet(user_query: str, mongo_store: bool = False, default_days: int = 5, db_path: str = "database/sample_data.sqlite3", **kwargs) -> str: 
    """
    This is a time series forecaster. The forecasting based on the `filter_data` and `feature_parameters` which is recieved from the `extract_keywords` tool.
    """
    agent_state = kwargs['state']
 
    if agent_state.state['feature_parameters'] :
        feature_parameters = agent_state.state['feature_parameters'] 
        filter_data = agent_state.state['filter_data'] 
    else :
        extracted_feature = extract_feature_keywords_for_sql_query(user_query = user_query) 
        extracted_date = extract_date_keywords(user_query = user_query, default_days = default_days)

        final_result = {**extracted_feature, **extracted_date}

        print(final_result)

        agent_state.state['feature_parameters'] = final_result
        filter_data = execute_sql_query(final_result, db_path)
        agent_state.state['filter_data'] = filter_data
        feature_parameters = agent_state.state['feature_parameters'] 
        filter_data = agent_state.state['filter_data'] 

    result = forecast_using_prophet_utils(filter_data, feature_parameters, mongo_store)
    return result