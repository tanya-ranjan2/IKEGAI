from langchain_core.utils.function_calling import convert_to_openai_function,convert_to_openai_tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ChatMessageHistory
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage,FunctionMessage,ToolMessage
import json
from dataclasses import dataclass

@dataclass
class StateDict:
    state={}
    config={}


class Agent:
    def __init__(self,role:str,desc:str,tools:list,llm,instruct_promt=None,output_prompt=None,state={},config:dict={},verbose:bool=False,execution_type:str="seq") -> None:
        """_summary_

        Args:
            role (str): Role of the Agent (ex: BD Admin, Librarian)
            desc (str): Description of the role 
            tools (list): list of tools associated with the agent
            llm (): Large Language Model
            config (dict, optional): arguments and default params for the tools. Defaults to {}.
            verbose (bool, optional): if Verbose will be on. Defaults to False.
            execution_type (str, optional): _description_. Defaults to "seq".
        """
        self.role=role
        self.verbose=verbose
        
        self.instruct_promt=instruct_promt
        self.output_prompt=output_prompt
        
        self.desc=desc
        self.tools=tools
        self.llm=llm
        self.execution_type=execution_type
        self.tool_calls=""
        # Converts the tools to openai formated tool_calls
        self.functions=[convert_to_openai_function(t) for t in tools]
        # Converts the tools to {tool_name: tool_func} format
        self.tools_action={tool_name['name']:func for tool_name,func in zip(self.functions,self.tools)}
        
        self.system_prompt=self._init_system_prompt_(role,desc)
        self.prompt=self._create_prompt_history_(self.system_prompt)
        self.chat_history = ChatMessageHistory()
        #comment Chain
        self.local_chat_history=self._set_local_history_()
        self.comment_prompt=self.__init__local_chat(self.instruct_promt,self.output_prompt)
        self.comment_chain=self.comment_prompt | self.llm
        
        #Followup Chain
        self.followup=self._init_followup_()
        self.followup_chain=self.followup | self.llm
        #create LLM chain 
        self.chain = self.prompt | self.llm.bind(functions=self.functions)
        self.intermediatory_steps={}
        self.config=config
        self.state_dict=StateDict()
        self.state_dict.config.update(state)
        
        
        
    def followup_qa(self):
        pass
    
    def _init_followup_(self):
        prompt=f'''Given the conversation Can you recommend 3 follow up questions. Use only the information from the conversation.
        '''
        chat_prompt=ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    prompt,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        return chat_prompt
        
    def _set_local_history_(self):
        return ChatMessageHistory()
    def dummy(self,query):
        return query
    def comment_tool(self):
        pass
    def _init_system_prompt_(self,role:str,desc:str)->str:
        """Initialize the Prompt

        Args:
            role (str): Role of the Agent
            desc (str): Description of the role 

        Returns:
            str: Returns the full prompt
        """
        prompt=f'''
        You are a function router AI. You will build a knowledge graph of functions and their inputs and outputs. 
        You will parse input query and find the correct sequence of functions to call to return the final correct result. 
        Since the functions may be executed in a sequential manner, you do not need to ask for confirmation on proceeding.
        Assume user intends to execute all the functions needed to answer the query.
        
        Your user facing role here is :{role}
        Your user facing job is: {desc}
        '''
        return prompt.format(role=role,desc=desc)
    
    
    def __init__local_chat(self,instruct_promt,output_prompt):
        prompt=f'''Summarize the following conversation in a few sentences. Use only the information from the conversation.
        '''
        if instruct_promt:
            prompt+=f"\n Here is the Instruction for your Job: {instruct_promt}"
        if output_prompt:
            prompt+=f"\n Note:{output_prompt}"
        print(prompt)
        chat_prompt=ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    prompt,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        return chat_prompt
    
    def _create_prompt_history_(self,system_prompt:str):
        """Create a conversational Prompt History

        Args:
            system_prompt (str): System Prompt

        Returns:
            ChatPromptTemplate: The Message Logs for LLM model
        """
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
    def _invoke_agent_(self,chat_history):
        """ Call the LLM model with conversation history

        Returns:
            Message: Output of the LLM Model
        """
        out=self.chain.invoke(
                {
                    "messages": chat_history.messages,
                }
            )
        return out
    
    def _invoke_comment_agent_(self,chat_history):
        """ Call the LLM model with conversation history

        Returns:
            Message: Output of the LLM Model
        """
        out=self.comment_chain.invoke(
                {
                    "messages": chat_history.messages,
                }
            )
        return out
    
    def _invoke_followup_agent_(self,chat_history):
        """ Call the LLM model with conversation history

        Returns:
            Message: Output of the LLM Model
        """
        out=self.followup_chain.invoke(
                {
                    "messages": chat_history.messages,
                }
            )
        return out
    
    def print_chat_history(self):
        """Prints Conversation History

        Returns:
            dict: Conversation History
        """
        json_chat_history=[]
        for i in self.chat_history.messages:
            json_chat_history.append({str(type(i).__name__):i.to_json()['kwargs']})
        return json_chat_history
    def _run_tool(self,function_info):
        
        tool=function_info["name"]
        tool_input=json.loads(function_info["arguments"])
        if self.execution_type=="parallel":
            if 'query' in tool_input:
                tool_input['query']=self.state_dict.state['input']
        #print(f"===TOOL INPUT===={tool_input}=========")
        if tool in self.config:
            tool_input.update(self.config[tool]["default_args"])
        
        ## For Community Tools 
        if '__arg1' in tool_input:
            tool_input['query'] = tool_input.pop('__arg1')
        else:
            tool_input['state']=self.state_dict
        
        tool_output =self.tools_action[tool].invoke(tool_input)
        #print(f"===TOOL OUTPUT===={tool_output}=========")
        return tool,tool_output
    
    def _execute_agent(self,query):
        self._set_local_history_()
        if len(self.tools)==0:
            raise Exception("No tools were added to the the Agent!! Please add tools to continue")
        # For Parallel and Sequencial Runs
        self.state_dict.state['input']=query
        # For Parallel and Sequencial Runs
        
        
        
        self.chat_history.add_user_message(query)
        self.local_chat_history.add_user_message(query)
        
        out=self._invoke_agent_(self.chat_history)
        
        self.chat_history.add_message(out)
        self.local_chat_history.add_message(out)
        
        #last_stable_output=out.content
        while "function_call" in out.additional_kwargs:
            if "function_call" in out.additional_kwargs:
                tool_name=out.additional_kwargs['function_call']['name']
                if tool_name==self.tool_calls:
                    self.chat_history.messages=self.chat_history.messages[:-1]
                    self.local_chat_history.messages=self.local_chat_history.messages[:-1]
                    break
                if self.verbose:
                    print("tool_call:",out.additional_kwargs)
                
                tool_name,tool_output=self._run_tool(out.additional_kwargs["function_call"])
                func_msg=FunctionMessage(name=tool_name,content=tool_output)
                
                self.chat_history.add_message(func_msg)
                self.local_chat_history.add_message(func_msg)
                
                self.intermediatory_steps[tool_name]=tool_output
                self.tool_calls=tool_name
                #last_stable_output=tool_output
            #check if more info is required
            self.chat_history.add_user_message("Is there any other tool that can be used for the task? Answer only in 'yes' or 'no'")
            out=self._invoke_agent_(self.chat_history)
            self.chat_history.add_message(out)
            #print(out)
            if out.content.lower() =="yes":
                out=self._invoke_agent_(self.chat_history)
                
                self.chat_history.add_message(out)
                self.local_chat_history.add_message(out)
                
        if self.execution_type=="parallel":
            context="\n".join([ k+": "+inter for k,inter in self.intermediatory_steps.items()])
            self.local_chat_history.add_ai_message(context)
            
        #commentary tool
        out=self._invoke_comment_agent_(self.local_chat_history)
        #followup tool
        followup=self._invoke_followup_agent_(self.local_chat_history)
        followup=followup.content.split('\n')
        return out.content,self.state_dict.state,followup
        