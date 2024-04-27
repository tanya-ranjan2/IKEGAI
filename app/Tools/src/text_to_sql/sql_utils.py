from langchain.chat_models import AzureChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool, QuerySQLCheckerTool
import pandas as pd
from langchain_community.agent_toolkits import SQLDatabaseToolkit
#from memory_profiler import profile

azure_llm = AzureChatOpenAI(
    openai_api_base = 'https://openai-lh.openai.azure.com/openai/',
    openai_api_version = '2023-06-01-preview',
    deployment_name = 'LH-GPT',
    openai_api_key = '312ff50d6d954023b8748232617327b6',
    temperature = 0
) 

# @profile
def execute_sql_query(feature_parameters: dict, db_path: str, meta_data: str = "") -> str :  
    db = SQLDatabase.from_uri("sqlite:///"+db_path) 
    all_features = feature_parameters["feature"]

    toolkit = SQLDatabaseToolkit(db=db, llm=azure_llm)
    context = toolkit.get_context()

    question = f"""
    You are a helpful AI assistant expert in querying SQL Database to find answers to user's question. \n
    Your task is to return all the values of date, {all_features} from the database \n
    and apply filter based on the filters given below :
    {feature_parameters["filter"]}.

    Consider the following meta data and database context to understand the tables : 
    ---------
    meta data : 
    {meta_data}
    ---------
    database context : 
    {context}

    NOTE: DON'T apply order or limit.
    """

    execute_query = QuerySQLDataBaseTool(db=db) 
    query_checker = QuerySQLCheckerTool(db=db, llm=azure_llm)
    write_query = create_sql_query_chain(azure_llm, db)

    chain = write_query | query_checker | execute_query 
    
    result = chain.invoke({
        "question": question 
    }) 

    return result 