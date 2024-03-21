from langchain_core.utils.function_calling import convert_to_openai_function,convert_to_openai_tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ChatMessageHistory
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage,FunctionMessage,ToolMessage
import json



#isSpecial tool= tool that has access to intermediate steps, A special tool will have **kwargs initiated
#obsersation : if argtype ==str it works else if list doesnot work

##Todo:
#if seq flag is off and multiple tools have been used --> use merge and comment | Same for agents
#forcefully put original query to each tool if 'parallel run'





class Agent:
    def __init__(self,role:str,desc:str,tools:list,llm,config:dict={},verbose:bool=False,execution_type:str="seq") -> None:
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
        self.desc=desc
        self.tools=tools
        self.llm=llm
        self.execution_type=execution_type
        # Converts the tools to openai formated tool_calls
        self.functions=[convert_to_openai_function(t) for t in tools]
        # Converts the tools to {tool_name: tool_func} format
        self.tools_action={tool_name['name']:func for tool_name,func in zip(self.functions,self.tools)}
        
        self.system_prompt=self._init_system_prompt_(role,desc)
        self.prompt=self._create_prompt_history_(self.system_prompt)
        self.chat_history = ChatMessageHistory()
        
        #create LLM chain 
        self.chain = self.prompt | self.llm.bind(functions=self.functions)
        self.intermediatory_steps={}
        self.config=config
        self.agent_state={}
        
        
    def dummy(self,query):
        return query
    
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
    def _invoke_agent_(self):
        """ Call the LLM model with conversation history

        Returns:
            Message: Output of the LLM Model
        """
        out=self.chain.invoke(
                {
                    "messages": self.chat_history.messages,
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
        #print(tool_input)
        if tool in self.config:
            tool_input.update(self.config[tool]["default_args"])
            if self.config[tool]["isSpecial"]:
                tool_input["intermediatory_steps"]=self.intermediatory_steps
                
    
        tool_output=self.tools_action[tool].invoke(tool_input)
        
        return tool,tool_output
    
    def _execute_agent(self,query):
        if len(self.tools)==0:
            raise Exception("No tools were added to the the Agent!! Please add tools to continue")
        # For Parallel and Sequencial Runs
        self.agent_state['input']=query
        # For Parallel and Sequencial Runs
        
        
        self.chat_history.add_user_message(query)
        out=self._invoke_agent_()
        self.chat_history.add_message(out)
        
        last_stable_output=out.content
        while "function_call" in out.additional_kwargs:
            if "function_call" in out.additional_kwargs:
                if self.verbose:
                    print("tool_call:",out.additional_kwargs)
                tool_name,tool_output=self._run_tool(out.additional_kwargs["function_call"])
                func_msg=FunctionMessage(name=tool_name,content=tool_output)
                self.chat_history.add_message(func_msg)
                self.intermediatory_steps[tool_name]=tool_output
                last_stable_output=tool_output
            #check if more info is required
            self.chat_history.add_user_message("Is there any other tool that can be used for the task? Answer only in 'yes' or 'no'")
            out=self._invoke_agent_()
            self.chat_history.add_message(out)
            #print(out)
            if out.content.lower() =="yes":
                out=self._invoke_agent_()
                self.chat_history.add_message(out)
            
        return last_stable_output
        