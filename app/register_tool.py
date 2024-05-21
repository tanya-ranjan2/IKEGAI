from Tools.utils.helper import convert_tool_into_master_schema


# Import the tool to register
from Tools.src.advanced_rag.advanced_rag_tools import advanced_rag

out=convert_tool_into_master_schema(advanced_rag)

print(out)

