from Tools.utils.helper import convert_tool_into_master_schema


# Import the tool to register
from Tools.src.rag.rag_tools import rag




out=convert_tool_into_master_schema(rag)

print(out)

