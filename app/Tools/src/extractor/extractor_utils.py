import json
import warnings
import numpy as np
warnings.filterwarnings("ignore")
from datetime import datetime, timedelta 
from langchain.chat_models import AzureChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_openai.embeddings.azure import AzureOpenAIEmbeddings
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool, QuerySQLCheckerTool
from memory_profiler import profile

llm_info = {
    "openai_api_base" : "https://openai-lh.openai.azure.com/openai/", 
    "openai_api_version" : "2023-06-01-preview", 
    "deployment_name" : "LH-GPT", 
    "openai_api_key" : "312ff50d6d954023b8748232617327b6", 
}

embedding_info = {
    "azure_endpoint" : 'https://openai-lh.openai.azure.com/',
    "openai_api_key" : '312ff50d6d954023b8748232617327b6',  
    "deployment" : 'LH-embedding', 
    "openai_api_version" : '2023-06-01-preview',
    "openai_api_type" : "azure"
}

# @profile
def extract_date_keywords(user_query: str, date_extractor_injection: list = [], default_days: int = 5) -> dict : 
    current_date = str(datetime.today().year) +'/'+ str(datetime.today().month) +'/'+ str(datetime.today().day) 
    
    extract_llm = AzureChatOpenAI(
        openai_api_base = llm_info["openai_api_base"], 
        openai_api_version = llm_info["openai_api_version"], 
        deployment_name = llm_info["deployment_name"], 
        openai_api_key = llm_info["openai_api_key"],
        temperature = 0, max_tokens = 200, verbose = True 
    )

    time_mapper = {
        "month" : 30, "year" : 365, "week" : 7, "quarter" : 3*30, 
        "fortnight" : 14, 'day' : 1
    }

    examples = [
        {
            "query" : "what will be the sales for next 1 month",
            "historical_date": "null",
            "historical_date_type": "null",
            "forecasting_date": str(10),
            "forecasting_date_type": "month"
        },
        {
            "query" : "based on data from 2021-04-02 predict sales of 2023-02-01",
            "historical_date": "2021-04-02",
            "historical_date_type": "date",
            "forecasting_date": "2023-02-01",
            "forecasting_date_type": "date"
        },
        {
            "query" : "based on data from last 1 year forecast for next one week",
            "historical_date": str(-1),
            "historical_date_type": "year",
            "forecasting_date": str(1),
            "forecasting_date_type": "week"
        },
        {
            "query" : "predict sales for 2024 based on 2023",
            "historical_date": "2023",
            "historical_date_type": "year",
            "forecasting_date": "2024",
            "forecasting_date_type": "year" 
        },
        {
            "query" : "predict sales for forthcoming year",
            "historical_date": "null",
            "historical_date_type": "null",
            "forecasting_date": str(1) ,
            "forecasting_date_type": "year" 
        }
    ]

    examples += date_extractor_injection
    
    example_selector = SemanticSimilarityExampleSelector.from_examples( 
        examples, 
        AzureOpenAIEmbeddings( 
            azure_endpoint = embedding_info["azure_endpoint"],
            openai_api_key = embedding_info["openai_api_key"],  
            deployment = embedding_info["deployment"], 
            openai_api_version = embedding_info["openai_api_version"],
            openai_api_type = embedding_info["openai_api_type"]
        ), 
        FAISS, 
        k = min(3, len(examples)),
    )

    # create an example template
    example_template = """
    User: {query}
        "historical_date" : "{historical_date}",
        "historical_date_type" : "{historical_date_type}",
        "forecasting_date" : "{forecasting_date}",
        "forecasting_date_type" : "{forecasting_date_type}"    
    """

    # create a prompt example from above template
    example_prompt = PromptTemplate(
        input_variables=["query", "historical_date", "historical_date_type", "forecasting_date", "forecasting_date_type"],
        template=example_template
    )

    # the prefix is our instructions
    prefix = f"""You are an AI Human Resource whose task is to extract following keywords mentioned below which
                can be further used for forecasting the variable.\
        
        "historical_date" : the date from which we have to filter the data. \
            if there is a specific date mentioned return the date \
            else if previous, last or past or similar terms mentioned use - infront of the integer \
            if no values present for historical data return null. \
            "the output must be a date, negative integer or null not a string" \
            
        "historical_date_type" : if the historical data is a specific date return date. \
            else if the historical data is year month, week or quarter, return the respective terms \
            if no values present for historical data return null \
            "the output must be a any of these date, month, year, quarter, week, null" \
        
        "forecasting_date" : the date till which we have to forecast the data. \
            if there is a specific date mentioned return the date \
            else if next, after or similar terms mentioned use positive integer.
            if no values present for forecasting data return null \
            "the output must be a date, positive integer or null not a string" \
            
        "forecasting_date_type" : if the forecasting data is a specific date return date. \ 
            else if the forecasting data is year month, week or quarter, return the respective terms
            if no values present for forecasting data return null \
            "the output must be a any of these date, month, year, quarter, week, null"   \
        
        Note: Please try to be specific about the keywords. Make sure to return only the JSON output.
        --------------------------------------------
        
        examples : 
    """ 
    
    # and the suffix our user input and output indicator
    suffix = """
    User: {query} 
        "historical_date" :  
        "historical_date_type" :
        "forecasting_date" :  
        "forecasting_date_type" :
    
    """

    # now create the few shot prompt template
    few_shot_prompt_template = FewShotPromptTemplate(
        example_selector = example_selector,
        example_prompt = example_prompt,
        prefix = prefix,
        suffix = suffix,
        input_variables = ["query"],
        example_separator = "\n\n"
    )

    # print(few_shot_prompt_template.format(query = user_query))
    extractor_date_response = extract_llm.invoke(
        few_shot_prompt_template.format(query = user_query)
    )

    extractor_date_response = "{" + extractor_date_response.content + "}"

    print('\ndate extractor llm output --> ', extractor_date_response, '\n')

    extractor_date_json_response = json.loads(extractor_date_response)

    # extract future data 
    forecasting_date_type = extractor_date_json_response["forecasting_date_type"]
    forecasting_date = extractor_date_json_response["forecasting_date"]

    future_date = None
    current_date = datetime.strptime(current_date,"%Y/%m/%d")

    #! if no future data present take default 1 month 
    if ((forecasting_date == "null") or (forecasting_date_type == "null") or (not forecasting_date or not forecasting_date_type)): 
        future_days = 30 
        if not future_date :
            future_date = np.datetime64((current_date + timedelta(days=future_days)).date())

    elif (forecasting_date != None) and (forecasting_date_type != None) : 
        if (forecasting_date_type != "date") :
            if len(str(forecasting_date)) >= 4 :
                future_days = 0 
                future_date = np.datetime64(forecasting_date)
            else :
                try :
                    future_days = time_mapper[forecasting_date_type] * (int)(forecasting_date)
                except : 
                    print('new measure found')
        elif (forecasting_date_type == "date") : 
            future_date = np.datetime64(forecasting_date)
            future_days = 0 

    if not future_date :
        future_date = np.datetime64((current_date + timedelta(days=future_days)).date())

    # print('\nfuture dates --> ', future_date, '\n')

    days_to_forecast = int(max((future_date - np.datetime64(current_date.date())) / np.timedelta64(1, 'D'), default_days))
    print('days to forecast --> ',days_to_forecast, '\n')
    
    extractor_date_json_response["days_to_forecast"] = days_to_forecast 
    return extractor_date_json_response

# @profile
def extract_feature_keywords(user_query: str, feature_extractor_injection: list = []) -> dict :
    extract_llm = AzureChatOpenAI(
        openai_api_base = llm_info["openai_api_base"], 
        openai_api_version = llm_info["openai_api_version"], 
        deployment_name = llm_info["deployment_name"], 
        openai_api_key = llm_info["openai_api_key"],
        temperature = 0, max_tokens = 200, verbose = True
    )

    examples = [
        {
            "query" : "what will be the revenue for next 1 month using quantity",
            "feature":"sales",
            "exogenous_variable": '["quantity"]'
        },
        {
            "query" : "based on cost_price and selling_price from 2021-04-02 predict sales of 2023-02-01",
            "feature":"sales",
            "exogenous_variable": '["cost_price","selling_price"]'
        },
        {
            "query" : "based on sales,quantity,cost and discount from last 1 year forecast profit for next one week",
            "feature":"profit",
            "exogenous_variable": '["sales", "quantity", "cost", "discount"]'
        },
        {
            "query" : "predict sales for 2024 based on 2023",
            "feature":"sales",
            "exogenous_variable": "[]"
        },
        {
            "query" : "predict inventory level for forthcoming year",
            "feature":"sales",
            "exogenous_variable": "[]"
        }
    ]

    examples += feature_extractor_injection
        
    example_selector = SemanticSimilarityExampleSelector.from_examples( 
            examples, 
            AzureOpenAIEmbeddings(
                azure_endpoint = embedding_info["azure_endpoint"],
                openai_api_key = embedding_info["openai_api_key"],  
                deployment = embedding_info["deployment"], 
                openai_api_version = embedding_info["openai_api_version"],
                openai_api_type = embedding_info["openai_api_type"]
            ), 
            FAISS, 
            k = min(3, len(examples)),
        )

    # create an example template
    example_template = """
        User: {query}
        "feature" : "{feature}" ,
        "exogenous_variable" : {exogenous_variable}    
        """

    # create a prompt example from above template
    example_prompt = PromptTemplate(
            input_variables=["query", "feature", "exogenous_variable"],
            template=example_template
        )
    
    
    # the prefix is our instructions
    prefix = f"""You are an AI Human Resource whose task is to extract keyword mentioned below which
                can be further used for forecasting the variable.

        "feature" : feature on which we want to perform forecasting. typically the column of the table.
        "exogenous_variable" : features to be used for prediction. The features should be in double quotes.
        
        Note: Please try to be specific about the keywords. The output should only have feature,
                exogenous_variable. And all the features should be in double quotes.
        
        ----------------------------------------------
        
        examples :
    """
    
    # and the suffix our user input and output indicator
    suffix = """
    User: {query}
    "feature" :  
    "exogenous_variable" :
    
    """

    # now create the few shot prompt template
    few_shot_prompt_template = FewShotPromptTemplate(
        example_selector = example_selector,
        example_prompt=example_prompt,
        prefix=prefix,
        suffix = suffix,
        input_variables=["query"],
        example_separator="\n\n"
    )

    #print(few_shot_prompt_template.format(query=user_query))
    extractor_feature_llm_response = extract_llm.invoke(
        few_shot_prompt_template.format(query=user_query)
    )

    extractor_feature_llm_response = "{" + extractor_feature_llm_response.content + "}"

    print('\nllm output --> ', extractor_feature_llm_response, '\n')

    extractor_feature_json_response = json.loads(extractor_feature_llm_response)

    return extractor_feature_json_response

# @profile
def extract_feature_keywords_for_sql_query(user_query: str, feature_extractor_injection: list = [], meta_data: str = "") -> dict :
    extract_llm = AzureChatOpenAI(
        openai_api_base = llm_info["openai_api_base"], 
        openai_api_version = llm_info["openai_api_version"], 
        deployment_name = llm_info["deployment_name"], 
        openai_api_key = llm_info["openai_api_key"],
        temperature = 0, max_tokens = 200, verbose = True
    )

    examples = [
        {
            "query" : "what will be the revenue for next 1 month using quantity",
            "feature":"sales",
            "filter": '[["quantity","all"]]'
        },
        {
            "query" : "forecast total order value for the next two months",
            "feature":"total order value",
            "filter": '[]'
        },
        {
            "query" : "what will be the total order value of next two months for packaging material of category l1",
            "feature":"profit",
            "filter": '[["category l1","packaging material"]]'
        },
        {
            "query" : "predict balance for 2024 based on 2023",
            "feature":"balance",
            "filter": '[]'
        },
        {
            "query" : "what will be the inventory of next 1 months for paper of category l3",
            "feature":"inventory",
            "filter": '[]'
        },
        {
            "query" : "predict the balance of next month where account type is investment",
            "feature":"balance",
            "filter": '[["account type","investment"]]'
        },
        {
            "query" : "predict the balance of next month where Material number l1 is M-20000000002268",
            "feature":"balance",
            "filter": '[["Material number","M-20000000002268"]]'
        },
        {
            "query" : "predict the balance for next 1 month",
            "feature":"balance",
            "filter": '[]'
        },
        {
            "query" : "total order value for next 2 months",
            "feature":"total order value",
            "filter": '[]'
        }
    ]

    examples += feature_extractor_injection
        
    example_selector = SemanticSimilarityExampleSelector.from_examples( 
            examples, 
            AzureOpenAIEmbeddings(
                azure_endpoint = embedding_info["azure_endpoint"],
                openai_api_key = embedding_info["openai_api_key"],  
                deployment = embedding_info["deployment"], 
                openai_api_version = embedding_info["openai_api_version"],
                openai_api_type = embedding_info["openai_api_type"]
            ), 
            FAISS, 
            k = min(3, len(examples)),
        )

    # create an example template
    example_template = """
        User: {query}
        "feature" : "{feature}" ,
        "filter" : {filter}    
        """

    # create a prompt example from above template
    example_prompt = PromptTemplate(
            input_variables=["query", "feature", "filter"],
            template=example_template
        )
    
    # the prefix is our instructions
    prefix = f"""
        You are an intelligent AI system whose task is to extract feature and filters from the `user query` for a sql query to filter data for forecasting.
        
        ----------------------------------------------
        TASK:
        - try to understand what if the feature of interset that we are trying to forecast and the required filters needed to generate sql query.

        ----------------------------------------------
        OUTPUT:
        - "feature" : feature on which we want to perform forecasting. typically a column of the table of numerical data type.
        - "filter" : additional filter to apply on to filter the dataframe. 
        
        NOTE : DO NOT include filters related to date, time, month, year, week, quarter, fortnight or day

        ----------------------------------------------
        CONTEXT: 
        Also use the following meta data to understand the database context and understand the `user query`. 
        {meta_data}

        ----------------------------------------------
        NOTE: Please try to be specific about the keywords. The output should only have feature and
        filter. And all the features should be in double quotes.
        
        ----------------------------------------------
        examples :
    """
    
    # and the suffix our user input and output indicator
    suffix = """
    User: {query}
    "feature" :  
    "filter" :
    
    """

    # now create the few shot prompt template
    few_shot_prompt_template = FewShotPromptTemplate(
        example_selector = example_selector,
        example_prompt=example_prompt,
        prefix=prefix,
        suffix = suffix,
        input_variables=["query"],
        example_separator="\n\n"
    )

    # print(few_shot_prompt_template.format(query=user_query))
    extractor_feature_llm_response = extract_llm.invoke(
        few_shot_prompt_template.format(query=user_query)
    )

    extractor_feature_llm_response = "{" + extractor_feature_llm_response.content + "}"
    print('\nfetaure extractor llm output --> ', extractor_feature_llm_response, '\n')

    extractor_feature_json_response = json.loads(extractor_feature_llm_response)
    return extractor_feature_json_response