from langchain_openai.chat_models import AzureChatOpenAI
import json


#local imports
from AgentExecutor.src import agents
from Tools.src.rag import rag_utils
from Tools.src.rag.rag_tools import rag,kg_rag
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
    #instruct_promt="Give Me The answers in Bullet points",
    output_prompt="If you dont have the Answer reply with 'I don't know'. Don't say anything else",
    llm=llm,
    tools=[eval(t) for t in agent_details[0]['tools']],
    config=agent_details[0]['func_config'],
    verbose=True,
    execution_type='parallel'
)

#print(rag_agent._execute_agent("who is indresh"))
print("OUTPUT:",rag_agent._execute_agent("Where does indresh work"))
