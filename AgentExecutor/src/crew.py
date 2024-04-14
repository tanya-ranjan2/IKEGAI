from langchain_core.utils.function_calling import convert_to_openai_function,convert_to_openai_tool

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ChatMessageHistory
from langchain.tools import BaseTool, StructuredTool, tool,Tool
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage,FunctionMessage,ToolMessage

import json

class Crew:
    def __init__(self,agents:list,llm,name:str=None,verbose=True):
        """Create a System of Agents that can autonomously work and solve problems

        Args:
            name (str): Name of the Crew
            agents (list): List agents
            llm (_type_): LLM 
            verbose (bool, optional): _description_. Defaults to True.

        
        """
        self.name="" if name is None else name
        self.agents=agents
        self.llm=llm
        self.verbose=verbose
        self.chat_history=ChatMessageHistory()
        self.system_prompt='''
        You are a function router AI. You will build a knowledge graph of functions and their inputs and outputs. 
        You will parse input query and find the correct sequence of functions to call to return the final correct result. 
        Since the functions may be executed in a sequential manner, you do not need to ask for confirmation on proceeding.
        Assume user intends to execute all the functions needed to answer the query.
        
        
        '''
        self.prompt=self._create_prompt_history_(self.system_prompt)
        self.agent_routers=[self._convert_agent_to_tools_(a) for a in self.agents]
        self.functions=[convert_to_openai_function(t) for t in self.agent_routers]
        self.agent_info={
            agent_name['name']:agent_func for agent_name, agent_func in zip(self.functions,self.agents)
        }
        self.chain = self.prompt | self.llm.bind(functions=self.functions)
        
        self.metadata={}
        self.followup=[]
        self.tokens={'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0}
    
    def _create_prompt_history_(self,system_prompt):
        chat_prompt=ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_prompt,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        return chat_prompt
    
    def _convert_agent_to_tools_(self,agent):
        t=StructuredTool.from_function(
            name="".join(agent.role.split()),
            description=agent.desc,
            func=agent.dummy,                      
        )
        return t
    def _invoke_agent_(self):
        out=self.chain.invoke(
                {
                    "messages": self.chat_history.messages,
                }
            )
        self.tokens['completion_tokens']=out.response_metadata['token_usage']['completion_tokens']
        self.tokens['prompt_tokens']=out.response_metadata['token_usage']['prompt_tokens']
        self.tokens['total_tokens']=out.response_metadata['token_usage']['total_tokens']
        return out
    def _run_tool(self,function_info,query):
        tool=function_info["name"]
        out,metadata,followup=self.agent_info[tool]._execute_agent(query)
        self.metadata.update(metadata)
        self.followup.extend(followup)
        return tool,out
        
    def run(self,query):
        self.chat_history.add_user_message(query)
        out=self._invoke_agent_()
        self.chat_history.add_message(out)
        last_stable_output=out.content
        if "function_call" in out.additional_kwargs:
            if self.verbose:
                print("agent_call:",out.additional_kwargs)
            tool_name,tool_output=self._run_tool(out.additional_kwargs["function_call"],query)
            
            func_msg=FunctionMessage(name=tool_name,content=tool_output)
            self.chat_history.add_message(func_msg)
            last_stable_output=tool_output
            
        return last_stable_output,self.metadata,self.followup