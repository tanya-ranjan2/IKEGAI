from langchain_openai.chat_models import AzureChatOpenAI
import json


#local imports
from AgentExecutor.src import agents,crew
from Tools.src.rag import rag_utils
from Tools.src.rag.rag_tools import rag,kg_rag,mergetool
from Tools.src.structured_tools.sql_tools import sql_generator,sql_executor

from _temp.config import OpenAIConfig
from dataclasses import asdict
from utils import parser
function_config={
    "rag":{
        "default_args":{
            "storage_name":"TBD/profile"
        },
        "isSpecial":False
    },
    "mergetool":{
        "default_args":{
            "llm": "func_llmbuilder(name='azureopenai')",
            "prev_tools": ['rag','kg_rag']
        },
        "isSpecial":True
    },
}
config_data=json.load(open('_temp/configManager.json'))
agent_details=parser.get_agent_details(config_data)

llm=AzureChatOpenAI(**asdict(OpenAIConfig()))


rag_agent= agents.Agent(
    role=agent_details[0]['role'],
    desc=agent_details[0]['desc'],
    llm=llm,
    tools=[eval(t) for t in agent_details[0]['tools']],
    config=agent_details[0]['func_config'],
    verbose=True
)

sql_agent= agents.Agent(
    role=agent_details[1]['role'],
    desc=agent_details[1]['desc'],
    llm=llm,
    tools=[eval(t) for t in agent_details[1]['tools']],
    config=agent_details[1]['func_config'],
    verbose=True
)


crew_of_agents=crew.Crew(
    
    agents=[rag_agent,sql_agent],
    llm=llm
)

#print(crew_of_agents.run("who is indresh"))
print(crew_of_agents.run("what was sales for 2023"))