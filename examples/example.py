import os
from langchain.agents import AgentExecutor
from langchain.agents import create_openai_tools_agent
from langchain.tools import Tool
from langchain.chat_models.openai import ChatOpenAI

from langchain import hub
from src.druva_native_workloads_ldk import (
    DruvaNativeWorkloadsAccountsTool,
    DruvaNativeWorkloadsPoliciesTool,
    DruvaNativeWorkloadsTasksTool,
    DruvaNativeWorkloadsResourcesTool
)

from langchain_community.utilities.serpapi import SerpAPIWrapper

os.environ['DRUVA_NATIVE_WORKLOADS_API_KEY'] = ''
os.environ['OPENAI_API_KEY'] = ''
os.environ['SERPAPI_API_KEY'] = ''

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

prompt = hub.pull("hwchase17/openai-functions-agent")

search = SerpAPIWrapper()

agent = create_openai_tools_agent(
    llm=llm,
    tools=[
        Tool(
            name="serpapi",
            func=search.run,
            description="useful for when you need to ask with search",
        ),
        DruvaNativeWorkloadsAccountsTool(),
        DruvaNativeWorkloadsTasksTool(),
        DruvaNativeWorkloadsPoliciesTool(),
        DruvaNativeWorkloadsResourcesTool(),
    ],
    prompt=prompt,
)

agent_executor = AgentExecutor(
    verbose=False,
    agent=agent,
    tools=[
        Tool(
            name="serpapi",
            func=search.run,
            description="useful for when you need to ask with search",
        ),
        DruvaNativeWorkloadsAccountsTool(),
        DruvaNativeWorkloadsTasksTool(),
        DruvaNativeWorkloadsPoliciesTool(),
        DruvaNativeWorkloadsResourcesTool(),
    ]
)

result = agent_executor.invoke({
    "input": "Get my native workloads resources, and then search the internet for any ongoing AWS outages that could affect them today 27/04/2024"
})

print(result)