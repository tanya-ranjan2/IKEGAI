from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain_openai.chat_models import AzureChatOpenAI

#local Imports
from Tools.src import tool_utils
from Tools.schema.structured_schema import SQLGeneratorTool,SQLExecutor


@tool(return_direct=True,args_schema=SQLGeneratorTool)
def sql_generator(query:str)->list:
    """Generate the SQL query from natural language `user query`. Run sql_executor after this"""
    return query


@tool(return_direct=False,args_schema=SQLExecutor)
def sql_executor(sql_query:str,creds:dict={})->list:
    """Executes the generated SQL query and returns the data. Once the `sql_generator` is called. This function must be called """
    print(creds)
    return "SQL Query Executed"