from utils import parser
from AgentExecutor.src import agents,crew

#IMPORT ALL TOOLS HERE
from Tools.src.rag.rag_tools import rag,kg_rag
from Tools.src.structured_tools.sql_tools import sql_generator,sql_executor
from Tools.src.community_tools.com_tool import DuckDuckGo, WikiPedia,YouTubeSearch,Arxiv,PythonRepl#,StackExchange
from Tools.src.extractor.extractor_tools import extract_keywords
from Tools.src.url_scrapper.scrapper_tool import scrapper
from Tools.src.advanced_rag.advanced_rag_tools import advanced_rag
from Tools.src.adv_ensemble_rag.adv_ensemble_rag_tools import advanced_rag_ensemble
from utils.llmops import llmbuilder

from _temp.config import Model_Mapping
def get_llm_details(config):
    if 'llm_params' not in config:
        raise Exception("LLM params not Updated !!!")
    return Model_Mapping[config["llm_params"]['llm_name']]
def create_agents(config,llm):
    """Create the Agents frrom configation

    Args:
        config (dict): Configation setting

    Returns:
        list: returns list of Agents
    """
    agent_details=parser.get_agent_details(config)
    #llm=llmbuilder(get_llm_details(config))
    all_agents=[]
    for agent_detail in agent_details:
        out_prompt=None
        if agent_detail['output_prompt']!='string':
            out_prompt=f'''
            - Give the responce in a {agent_detail['output_prompt']['tone']} tone
            '''
        _agent_= agents.Agent(
            role=agent_detail['role'],
            desc=agent_detail['desc'],
            instruct_promt= agent_detail['instruction_prompt'] if agent_detail['instruction_prompt']!='string' else None,
            output_prompt=out_prompt,
            llm=llm,
            tools=[eval(t) for t in agent_detail['tools']],
            config=agent_detail['func_config'],
            verbose=True,
            state=config
        )
        all_agents.append(_agent_)
    return all_agents

