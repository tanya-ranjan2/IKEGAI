
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
        "isSpecial":True
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