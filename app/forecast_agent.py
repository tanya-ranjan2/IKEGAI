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

config_data=json.load(open('_temp/configManager_for_forecasting.json'))
agent_details=parser.get_agent_details(config_data)

print(agent_details)
llm=AzureChatOpenAI(**asdict(OpenAIConfig()))

forecasting_agent= agents.Agent(
    role = agent_details[0]['role'],
    desc = agent_details[0]['desc'],
    #instruct_promt="Give Me The answers in Bullet points",
    output_prompt = "If you dont have the Answer reply with 'I don't know'. Don't say anything else",
    llm = llm, 
    tools = [extract_keywords],
    config = agent_details[0]['func_config'],
    verbose = True,
    execution_type = 'parallel'
)
 
user_input = input("enter your query : ")
print("OUTPUT:",forecasting_agent._execute_agent(user_input))