
## Folder Structure

```bash
├── schema [Contains all pydantic schemas]
│   ├── <tool_name>_schema.py [Contains schemas or dataclasses for specific tool]
├── src
│   ├── tool_utils.py [Contains functions for general usage accross tools]
│   ├── <tool_name>
│   │   ├── <tool_name>_utils.py [Contains utility functions for specific tool]
│   │   ├── <tool_name>.py [Code for actual tools]
└── READM.MD
```

## Define a tool

```python

from langchain.tools import tool
from langchain.pydantic_v1 import BaseModel, Field

# Difine Schema for Tool
class DummyTool(BaseModel):
    query: str = Field(description="original `user input`")

#define the tool
@tool(args_schema=DummyTool)
def dummy(query:str)->list:
    """Returns results from searching documents"""
    return "Dummy Responce"
```

**Note** : 
- all tools should have decorator `@tool` with `args_schema` parameter
- all tools should have a `doctring` which describes the function and it should be in `""" doctring """`
- for a tool which has arguments as options like "azureopenai" and "hugginface " use `Literal['azureopenai','hugginface']` in the schema defination
  - example : `llm: Literal['azureopenai','hugginface'] = Field(description="description")`
- 

#### For cases where you have to execute dynamic functions (ex: `func_llmbuilder('azureopenai')`)
if your tool is using a where you need to execute a dynamic function from user include the following in your tool

```python
from Tools.src import tool_utils

#tool defination
'''
@tool(args_schema=MergeTool)
def mergetool(query:str,llm:str=None)->str:
'''

is_func=tool_utils.check_if_func_call_required(llm) 
if is_func:
    llm_func=eval(is_func)
```

full example

```python
function_config={
    "mergetool":{
        "default_args":{
            "llm": "func_llmbuilder(name='azureopenai')",
            
        },
    },
}
@tool
def mergetool(query:str,llm:str=None)->str:
    """Merge the output of other tools and gives response to the user."""
    #print(query,llm,prev_tools,intermediatory_steps)
    
    is_func=tool_utils.check_if_func_call_required(llm)
    if is_func:
        llm_func=eval(is_func)
    out=chatmodel(query,llm_func)
    return out.content
    
```


## `Important`

Once the tool in created:
- Add the tool info to AgentExecutor.utils.helper
- Every tool should have a argument called `query` , this is the original user query
```python
#IMPORT ALL TOOLS HERE
from Tools.src.rag.rag_tools import rag,kg_rag,mergetool
from Tools.src.structured_tools.sql_tools import sql_generator,sql_executor


```


Every tool has access to `state` variable that can store information that would not be passed to the LLM

# StateFull Tools

```python
class RagTool(BaseModel, extra=Extra.allow):
    query: str = Field(description="original `user input`")
    storage_name: str = Field(description="Name of the vector database to be Searched")


@tool(return_direct=False,args_schema=RagTool)
def rag(query:str,storage_name:str,**kwargs)->list:
    """Returns results from searching documents in vector database"""
    # For Acessing internal State of tools
    agent_state=kwargs['state'].state

    # For Acessing internal configation of Agent
     agent_config=kwargs['state'].config

    embeddings=rag_utils.load_embeddings()
    db=rag_utils.load_vectordb(storage_name,embeddings)
    
    documents=db.invoke(query)
    reference=[i.metadata for i in documents]
    agent_state.state['rag']=reference
    return rag_utils.make_context(documents)
```

### For StateFull Tools the ToolSchema should have 
- `extra=Extra.allow` as a intehited variable
- the tool defination should have `**kwargs`
- you can access the state using `kwargs['state']`
- <b>Remember:</b> this state will be accessable to all the tools and agents


### Register a tool

Use `register_tool.py` to get Json Format for the tool

you can make changes required to the tool, before pushing into to the master API

Once you run the below utility

```python
from Tools.utils.helper import convert_tool_into_master_schema
import json


# Import the tool to register
from Tools.src.rag.rag_tools import rag

out=convert_tool_into_master_schema(rag)

print(json.dumps(out, indent=4))
```

you will get a json Format like below. You can make changes to the same 

```json
{
    "tool_name": "rag",
    "tool_desc": "Returns results from searching documents in vector database",
    "fields": [
        {
            "name": "query",
            "desc": "original `user input`",
            "type": "text",
            "value": null,
            "isMandatory": true
        },
        {
            "name": "topk",
            "desc": "No of document chunks to retrived. By default it is 3.",
            "type": "number",
            "value": 3,
            "isMandatory": false
        },
        {
            "name": "llm",
            "desc": "Name of LLM",
            "type": "selectbox",
            "value": [
                "AzureOpenAI",
                "Hugginface"
            ],
            "isMandatory": true
        }
    ]
}
```
