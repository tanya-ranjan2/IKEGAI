from langchain_openai import AzureChatOpenAI
from langchain_groq import ChatGroq




#<CODEBLOCK>
from _temp.config import OpenAIConfig, MistralConfig, Llama3Config
from dataclasses import asdict
#<CODEBLOCK>


def llmbuilder(name):
    if name =="azureopenai":
        open_ai=OpenAIConfig()
        return AzureChatOpenAI(**asdict(open_ai))
    if name == "mistral" : 
        mistral = MistralConfig()
        print("-"*10 + "using mistral")
        return ChatGroq(**asdict(mistral))
    if name == "llama-3" : 
        print("-"*10 + "using llama-3")
        llama3 = Llama3Config()
        return ChatGroq(**asdict(llama3))
    else:
        return None


