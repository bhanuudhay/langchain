from dotenv import load_dotenv
from pydantic.types import T

load_dotenv()

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
# from tavily import TavilyClient
from langchain_tavily import TavilySearch

# tavily = TavilyClient()

# @tool
# def search(query: str):
#     """
#     Tool that search over the internet 
#     Args:
#         query: The query to search for 
#     Returns:
#         The search result
#     """
#     print(f"Searching for {query}")
#     return tavily.search(query=query)
    
llm  = ChatOllama(model="llama3.1:8b")
tools = [TavilySearch()]
agent = create_agent(model=llm,tools=tools)

def main():
    print("hello world")
    
    result = agent.invoke({
        "messages": [HumanMessage(content="search  for 3 job posting for backend developer on linked and other platform")]
    })
    print(result["messages"][-1].content)
    
    
if __name__ == "__main__":
    main()