from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain_openai.chat_models import AzureChatOpenAI

#local Imports
from Tools.src import tool_utils
from Tools.schema.extractor_schema import ExtractKeywords
from Tools.src.extractor.extractor_utils import extract_date_keywords, extract_feature_keywords_for_sql_query
from Tools.src.text_to_sql.sql_utils import execute_sql_query 
from Tools.src.forecasting.forecasting_utils import forecast_using_prophet_utils 
from utils.llmops import llmbuilder
import pandas as pd

@tool(return_direct = True, args_schema=ExtractKeywords)
def extract_keywords(user_query: str, default_days: int = 5, db_path: str = "database/sample_data.sqlite3", meta_data_path: str = "database/meta_data.txt", **kwargs) -> str: 
    """
    Generate the SQL query from natural language user query and do the forecasting.
    """
    print("input to the function --> ", user_query)
    agent_state = kwargs['state'] 

    user_query = user_query.lower()
    with open(meta_data_path, "r+") as f: 
        meta_data = f.read()

    try : 
        extracted_feature = extract_feature_keywords_for_sql_query(user_query = user_query, meta_data = meta_data) 
        extracted_date = extract_date_keywords(user_query = user_query, default_days = default_days)

        # ? remove date filters from the list 
        restricted_entity, new_filter = {"month", "year", "week", "quarter", "fortnight", "day", "date"}, []
        if extracted_feature["filter"] :
            for filter_list in extracted_feature["filter"] : 
                flag = True
                if type(filter_list) == list :
                    for entity in restricted_entity : 
                        for keyword in filter_list :  
                            if entity in keyword.lower() :
                                flag = False 

                    if flag : 
                        new_filter.append(filter_list)

        extracted_feature = {
            "feature" : extracted_feature["feature"], 
            "filter" : new_filter
        }

        # create final result dict 
        print(extracted_feature)
        final_result = {**extracted_feature, **extracted_date}

        agent_state.state['feature_parameters'] = final_result
        filter_data = execute_sql_query(final_result, db_path, meta_data = meta_data)
        agent_state.state['filter_data'] = filter_data

        table_creation, chart_creation, chart_config, accuracy_metrics, to_chop = forecast_using_prophet_utils(filter_data, final_result)

        try :
            agent_state.state['table'] = table_creation.to_dict(orient="tight")
            agent_state.state['data'] = chart_creation
            agent_state.state['chart_config'] = chart_config 
            agent_state.state['accuracy_metrics'] = accuracy_metrics 
            agent_state.state['forecasted_period'] = to_chop 

            print(table_creation.tail(int(to_chop)))
            return table_creation.tail(int(to_chop)).to_markdown()
        except : 
            return table_creation
    except : 
        return "Unable to extract relevant information from the query. Try asking some different questions..."