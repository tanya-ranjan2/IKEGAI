from Tools.utils.helper import convert_tool_into_master_schema


# Import the tool to register
from Tools.src.rag.rag_tools import rag
from Tools.src.url_scrapper.scrapper_tool import scrapper

out=convert_tool_into_master_schema(scrapper)

print(out)

