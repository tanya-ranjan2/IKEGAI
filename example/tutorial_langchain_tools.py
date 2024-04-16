from langchain_openai.chat_models import AzureChatOpenAI
import json


#local imports

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools.wikidata.tool import WikidataAPIWrapper, WikidataQueryRun

from AgentExecutor.src import agents
from _temp.config import OpenAIConfig
from dataclasses import asdict
from utils import parser

search = DuckDuckGoSearchRun()
wikidata = WikidataQueryRun(api_wrapper=WikidataAPIWrapper())
tools=[search,wikidata]


API_KEY="312ff50d6d954023b8748232617327b6"
llm=AzureChatOpenAI(**asdict(OpenAIConfig()))


rag_agent= agents.Agent(
    role="Search Engine",
    desc="You are a Search Engine , who will find Infomation about subject from the internet",
    #instruct_promt="Give Me The answers in Bullet points",
    output_prompt="If you dont have the Answer reply with 'I don't know'. Don't say anything else",
    llm=llm,
    tools=tools,
    config={},
    verbose=True,
    execution_type='parallel'
)


print(rag_agent._execute_agent("who is indresh bhattacharya"))
#print("OUTPUT:",rag_agent._execute_agent("Where does indresh work"))
