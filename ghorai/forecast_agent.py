from langchain_openai.chat_models import AzureChatOpenAI
import json

#local imports
from AgentExecutor.src import agents 
from Tools.src.rag import rag_utils 
from Tools.src.forecasting.forecasting_tools import forecast_using_prophet 
from Tools.src.extractor.extractor_tools import extract_keywords
from _temp.config import OpenAIConfig
from dataclasses import asdict
from utils import parser
from langchain_community.utilities import SQLDatabase

config_data=json.load(open('_temp/configManager.json'))
agent_details=parser.get_agent_details(config_data)

print(agent_details)
llm=AzureChatOpenAI(**asdict(OpenAIConfig()))


forecasting_agent= agents.Agent(
    role = agent_details[0]['role'],
    desc = agent_details[0]['desc'],
    #instruct_promt="Give Me The answers in Bullet points",
    output_prompt = "If you dont have the Answer reply with 'I don't know'. Don't say anything else",
    llm = llm, 
    tools = [extract_keywords, forecast_using_prophet],
    config = agent_details[0]['func_config'],
    verbose = True,
    execution_type = 'sequential'
)
 
print("OUTPUT:",forecasting_agent._execute_agent("predict the balance for next 1 month"))

#  // instruction  
# // tool doc string 
#  // tool field description 

# // \n\n---------------\nINSTRUCTION: first execute the `extract_keywords` tool. next pass the output into the `text_to_sql` tool finally pass the filtered result into `forecast_using_prophet` tool.
# // "Your job is to first find out context keywords from the `user_query` using `extract_keywords` tool, next generate and execute SQL query based on the extracted context keywords from `extract_keywords` tool using `text_to_sql` tool and finally forecast based on the filtered data generated from `text_to_sql` tool using the `forecast_using_prophet`.\nNOTE: DONOT change the `user_query` and pass it as it is into the `extract_keywords` tool. Run all the tools", 
# // "desc" : "Your job is to first find out context keywords from the `user_query`, next generate and execute SQL query based on the extracted context keywords from `user_query` and finally forecast based on the filtered data.\nNOTE: DO NOT change the `user_query` and pass it as it is into the `extract_keywords` tool. Run all the tools", 

# // "desc" : "Your job is to first find out context keywords from the user input, generate and execute SQL queries from the `user query` and finally forecast based on the filtered data. \n NOTE: DONOT change the `user_query` and pass it as it is into the tools and run all the tools, and donot ask the users for running the tools", 

# "Your job is to forecast the values using the tool `forecast_using_prophet`. \nfirst find out context keywords from the `user_input` then generate and execute SQL query to filter the data using `extract_keywords` then forecast based on the filtered data. \nNOTE: DONOT change the `user_query` and pass it as it is into the tools and run all the tools"