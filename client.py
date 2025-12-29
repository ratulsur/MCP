from langchain_mcp_adapters import MultiServerMCPClient
from langchain.agents import create_react_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
import asyncio
import os

async def main():
    client = MultiServerMCPClient(
        {
            "calculator": {
                "command": "python",
                "args": ["calculator.py"],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://127.0.0.1:8000",
                "transport": "streamable_http",
            },
        }
    )

    tools = await client.get_tools()

    model = ChatGroq(model="qwen-qwq-32b")
    agent = create_react_agent(tools, model)

    