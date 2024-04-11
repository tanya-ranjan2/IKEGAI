from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain_openai.chat_models import AzureChatOpenAI

#local Imports
from Tools.src import tool_utils
from Tools.schema.forecasting_schema import ForecastingUsingProphet
from Tools.src.forecasting.forecasting_utils import forecast_using_prophet
from utils.llmops import llmbuilder
import pandas as pd
 
@tool(return_direct = False, args_schema=ForecastingUsingProphet)
def forecast_using_prophet(filter_data, feature_parameters, **kwargs) -> str: 
    """
    This is a time series forecaster. The forecasting based on the `filter_data` and `feature_parameters` which is recieved from the `extract_keywords` tool.
    """
    agent_state = kwargs['state']
    # feature_parameters = agent_state.state['feature_parameters'] 
    # filter_data = agent_state.state['filter_data'] 

    result = forecast_using_prophet(filter_data, feature_parameters)
    return result