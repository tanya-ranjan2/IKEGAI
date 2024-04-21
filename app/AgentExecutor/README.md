
## QuickGuide

### Running an Agent

NOTE:
`1. Agents have Inbuild Memory so they store converstion`

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
- `execution_type`: `sequential` or `parallel` 
  - if `parallel` it will run the tools parallely and Merge the output of the tools


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

## Multi-Agent

```python
from AgentExecutor.src import agents,crew
agent_list=[agent_1,agent_2]
crew_of_agents=crew.Crew(
    name="Crew Name"
    agents=agent_list,
    llm=llm
)

print(crew_of_agents.run("who is indresh"))
```

## Using Langchain Community Tools

```python
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


llm=AzureChatOpenAI(**asdict(OpenAIConfig()))


agent= agents.Agent(
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


print(agent._execute_agent("who is indresh bhattacharya"))
#print("OUTPUT:",rag_agent._execute_agent("Where does indresh work"))

```

### To Add Coversation History (Only incase you want to do it forcefully)


This will reset the Previous conversation and add user defined conversation

NOTE: Only works with `Agents` not `Crew[multiple Agents]`

```python
from AgentExectutor.src import agents

prev_conversation=[{'user_query':"This is a user query","response":"this is a LLM response"}]

agent=agents.Agent(
    role='Librarian',
    desc='''You search documents for answers and give the answers, always use the tools to search documents.
            Use all the tools required without asking the user.
           Use all possible search tools and finally merge the serch results to respond.
            Don't Change the `user input` for the for the search tools.''',
    llm=llm,
    tools=[rag,kg_rag,mergetool],
    config=function_config,
    verbose=True,
    prev_conversation=prev_conversation
)
```

or 

```python
from AgentExectutor.src import agents

prev_conversation=[{'user_query':"This is a user query","response":"this is a LLM response"}]

agent=agents.Agent(
    role='Librarian',
    desc='''You search documents for answers and give the answers, always use the tools to search documents.
            Use all the tools required without asking the user.
           Use all possible search tools and finally merge the serch results to respond.
            Don't Change the `user input` for the for the search tools.''',
    llm=llm,
    tools=[rag,kg_rag,mergetool],
    config=function_config,
    verbose=True,
    
)

agent.set_previous_conversions(prev_conversation)
```