import os 
import asyncio 
from dotenv import load_dotenv 
from langchain_mcp_adapters.client import MultiServerMCPClient 
from langchain.agents import create_agent 
from langchain_groq import ChatGroq


from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    raise RuntimeError("Missing GROQ_API_KEY in .env or environment")


async def main():
    async with MultiServerMCPClient(
        {
            "calculator": {
                "command": "python",
                "args": ["calculator.py"],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://127.0.0.1:8001/mcp",   # <-- make this distinct
                "transport": "streamable-http",       # <-- match your server spelling
            },
            "arxiv": {
                "url": "http://127.0.0.1:8002/mcp",   # <-- make this distinct
                "transport": "streamable-http",
            },
        }
    ) as client:
        tools = await client.get_tools()

        llm = ChatGroq(model="openai/gpt-oss-120b")

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Use tools when useful."),
            ("human", "{input}"),
        ])

        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        result = await executor.ainvoke({"input": "what is an embedding?"})
        print(result["output"])


if __name__ == "__main__":
    asyncio.run(main())
