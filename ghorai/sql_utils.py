from langchain.chat_models import AzureChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool, QuerySQLCheckerTool
import pandas as pd

azure_llm = AzureChatOpenAI(
    openai_api_base = 'https://openai-lh.openai.azure.com/openai/',
    openai_api_version = '2023-06-01-preview',
    deployment_name = 'LH-GPT',
    openai_api_key = '312ff50d6d954023b8748232617327b6',
    temperature = 0
) 

def execute_sql_query(feature_parameters: dict) -> str :
    # print('inside utils --> ', feature_parameters)
    db = SQLDatabase.from_uri("sqlite:///Tools/src/text_to_sql/database/sample_data.sqlite3") 
    # feature_parameters = eval(feature_parameters)
    # if date_params['historical_date_type'] == 'null' : 
    #     num_features = 'all'
    #     history = ""
    # else : 
    #     num_features = ""
    #     history = "for the last " + str(date_params['historical_date']) + str(date_params['historical_date_type'])

    all_features = feature_parameters["exogenous_variable"] + [feature_parameters["feature"]]

    print(all_features)

    question = f"""
    Give me all the values of date, {all_features} from the database.
    """

    execute_query = QuerySQLDataBaseTool(db=db) 
    query_checker = QuerySQLCheckerTool(db=db, llm=azure_llm)
    write_query = create_sql_query_chain(azure_llm, db)
    
    chain = write_query | query_checker | execute_query
    
    result = chain.invoke({
        "question": question 
    }) 

    return result 