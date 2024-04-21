from Tools.utils.helper import convert_tool_into_master_schema


# Import the tool to register
from Tools.src.rag.rag_tools import rag
from Tools.src.forecasting.forecasting_tools import forecast_using_prophet

out=convert_tool_into_master_schema(forecast_using_prophet)

print(out)

