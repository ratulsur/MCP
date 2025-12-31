import os
import asyncio
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_groq import ChatGroq

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    raise RuntimeError("Missing GROQ_API_KEY in .env or environment")
os.environ["GROQ_API_KEY"] = groq_key


async def main():
    client = MultiServerMCPClient(
        {
            "calculator": {
                "command": "python",
                "args": ["calculator.py"],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            },
            "arxiv": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            },
        }
    )

    tools = await client.get_tools()

    model = ChatGroq(model="openai/gpt-oss-120b")
    agent = create_agent(model, tools)

    response = await agent.ainvoke({"messages": [("user", "what is an embedding?")]})
    print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
