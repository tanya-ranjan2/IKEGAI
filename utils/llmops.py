from langchain_openai import AzureChatOpenAI



#<CODEBLOCK>
from _temp.config import OpenAIConfig
from dataclasses import asdict
#<CODEBLOCK>


def llmbuilder(name):
    if name =="azureopenai":
        open_ai=OpenAIConfig()
        return AzureChatOpenAI(**asdict(open_ai))
    else:
        return None



