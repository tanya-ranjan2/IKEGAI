from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain_community.tools.wikidata.tool import WikidataAPIWrapper, WikidataQueryRun
from langchain.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from langchain_community.tools import YouTubeSearchTool
from langchain_community.utilities import ArxivAPIWrapper
from langchain_community.utilities import StackExchangeAPIWrapper

from langchain.agents import Tool
from langchain_experimental.utilities import PythonREPL




WikiPedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())



DuckDuckGo=DuckDuckGoSearchRun()
YouTubeSearch=YouTubeSearchTool()
Arxiv = ArxivAPIWrapper()
StackExchange = StackExchangeAPIWrapper()

PythonRepl = PythonREPL()
