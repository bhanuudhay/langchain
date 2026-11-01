from dotenv import load_dotenv

load_dotenv()


from typing import List
from pydantic import BaseModel, Field

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_tavily import TavilySearch


class Source(BaseModel):
    """ Schema for a source used by the agent """
    url: str = Field(description="The url of the sources")

class AgentResponse(BaseModel):
    """ Schema for a the agent response"""
    anwser: str = Field(description="The agent's anwser to the query")
    sources: List[Source] = Field(default_factory=list , description="List of sources used to generate the anwser")

llm  = ChatOllama(model="llama3.1:8b")
tools = [TavilySearch()]
agent = create_agent(model=llm,tools=tools,response_format=AgentResponse)

def main():
    print("hello world")
    
    result = agent.invoke({
        "messages": [HumanMessage(content="search  for 3 job posting for backend developer on linked and other platform")]
    })
    print(result)
    
    
if __name__ == "__main__":
    main()