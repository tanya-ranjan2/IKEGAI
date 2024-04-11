from langchain_openai.chat_models import AzureChatOpenAI
import json


#local imports
from AgentExectutor.src import agents
from Tools.src.rag import rag_utils
from Tools.src.rag.rag_tools import rag,kg_rag,mergetool
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

API_KEY="312ff50d6d954023b8748232617327b6"
llm=AzureChatOpenAI(api_key=API_KEY,
                    azure_endpoint="https://openai-lh.openai.azure.com/",
                    openai_api_version="2024-02-15-preview",
                    azure_deployment="test",
                    #azure_deployment="gpt-35-turbo-0613",
                    temperature=0
                   )


rag_agent= agents.Agent(
    role=agent_details[0]['role'],
    desc=agent_details[0]['desc'],
    llm=llm,
    tools=[rag,kg_rag,mergetool],
    config=agent_details[0]['func_config'],
    verbose=True
)

print(rag_agent._execute_agent("who is indresh"))
