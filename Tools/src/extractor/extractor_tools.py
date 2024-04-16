from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain_openai.chat_models import AzureChatOpenAI

#local Imports
from Tools.src import tool_utils
from Tools.schema.extractor_schema import ExtractKeywords
from Tools.src.extractor.extractor_utils import extract_date_keywords, extract_feature_keywords, extract_feature_keywords_for_sql_query
from Tools.src.text_to_sql.sql_utils import execute_sql_query 
from Tools.src.forecasting.forecasting_utils import forecast_using_prophet_utils 
from utils.llmops import llmbuilder
import pandas as pd

@tool(return_direct = True, args_schema=ExtractKeywords)
def extract_keywords(user_query: str, default_days: int = 5, db_path: str = "database/sample_data.sqlite3", **kwargs) -> str: 
    """
    Generate the SQL query from natural language user query. Run forecast_using_prophet after this.
    """
    print("input to the function --> ", user_query)
    agent_state = kwargs['state'] 
    extracted_feature = extract_feature_keywords_for_sql_query(user_query = user_query) 
    extracted_date = extract_date_keywords(user_query = user_query, default_days = default_days)

    final_result = {**extracted_feature, **extracted_date}

    print(final_result)

    agent_state.state['feature_parameters'] = final_result
    filter_data = execute_sql_query(final_result, db_path)
    agent_state.state['filter_data'] = filter_data

    table_creation, chart_creation, chart_config = forecast_using_prophet_utils(filter_data, final_result)

    agent_state.state['table'] = table_creation.to_dict(orient="tight")
    agent_state.state['data'] = chart_creation
    agent_state.state['chart_config'] = chart_config
    print(table_creation.tail().to_markdown())
    return table_creation.tail().to_markdown()
