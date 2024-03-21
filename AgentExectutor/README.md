




## TODO

- [ ] Modify Agent class, remove `isSpecial` flag to implement the above
  - [ ] if `execution_type` is `'sequential'` : the first tool will get the actual query the others will receive the LLM suggested args
  - [ ] if  `execution_type` is `'parallel'` : all the tools will receive the user query. `mergeFunction` with merge the output of all the tools and finally commentery will be given
  - [ ] add a `commentry` function at the end of each agent, which can summarize the whole ReAct execution to provide the summary
    - [ ] this can be controled by flag `return_direct` on agent initialization
  - [ ] Add additional details on `verbose`




## QuickGuide

### Running an Agent

```python
from langchain_openai.chat_models import AzureChatOpenAI
import json


#local imports
from AgentExectutor.src import agents
from Tools.src import rag_utils
from Tools.src.rag_tools import rag,kg_rag,mergetool
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



llm=AzureChatOpenAI(api_key=API_KEY,
                    azure_endpoint=DEPLOYMENT_URL,
                    openai_api_version=API_VERSION,
                    azure_deployment=DEPLOYMENT_NAME,
                    #azure_deployment="gpt-35-turbo-0613",
                    temperature=0
                   )


rag_agent= agents.Agent(
    role='Librarian',
    desc='''You search documents for answers and give the answers, always use the tools to search documents.
            Use all the tools required without asking the user.
           Use all possible search tools and finally merge the serch results to respond.
            Don't Change the `user input` for the for the search tools.''',
    llm=llm,
    tools=[rag,kg_rag,mergetool],
    config=function_config,
    verbose=True
)

print(rag_agent._execute_agent("who is indresh"))

```

to pass a `parameterised function` as argument, without hardcoding
: if you need a pass a function a start the argument name with `'func_'` followed by function name and params. ex: `'llmbuilder'` is a function that takes `name` as argument `'llmbuilder(name:str)'`. So to define that in default args you can use `func_llmbuilder(name='azureopenai')`


## Define a Agent

Agent takes in 4 required arguments:

- `role`: role of the agent
- `desc`: What is is supposed to do
- `llm`: Configaration for the LLM
- `tools`: List of tools [for details look at Tools> README]
```python
from AgentExectutor.src import agents

agent=agents.Agent(
    role='Librarian',
    desc='''You search documents for answers and give the answers, always use the tools to search documents.
            Use all the tools required without asking the user.
           Use all possible search tools and finally merge the serch results to respond.
            Don't Change the `user input` for the for the search tools.''',
    llm=llm,
    tools=[rag,kg_rag,mergetool],
    config=function_config,
    verbose=True
)
```
To Execute an Agent

```python
agent._execute_agent(query)
```


**Note**: `"isSpecial":True` is used when the tool needs intermediatory steps. 
- if `"isSpecial":True` then in function defination should have `intermediatory_steps` as a argument
```python
function_config={
    "dummy":{
        "isSpecial":True
    },
}
def dummy(query,intermediatory_steps:dict)
```