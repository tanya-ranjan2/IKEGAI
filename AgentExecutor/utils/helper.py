from utils import parser
from AgentExecutor.src import agents,crew

#IMPORT ALL TOOLS HERE
from Tools.src.rag.rag_tools import rag,kg_rag
from Tools.src.structured_tools.sql_tools import sql_generator,sql_executor

from utils.llmops import llmbuilder

def create_agents(config):
    agent_details=parser.get_agent_details(config)
    llm=llmbuilder("azureopenai")
    all_agents=[]
    for agent_detail in agent_details:
        
        _agent_= agents.Agent(
            role=agent_detail['role'],
            desc=agent_detail['desc'],
            instruct_promt=agent_detail['instruct_promt'],
            output_prompt=agent_detail['output_prompt'],
            llm=llm,
            tools=[eval(t) for t in agent_detail['tools']],
            config=agent_detail['func_config'],
            verbose=True
        )
        all_agents.append(_agent_)
    return all_agents

