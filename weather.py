from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather MCP")

@mcp.tool()

async def weather_updates(location, query)-> str:
    """
    Docstring for weather_updates
    
    :param location: Description
    :param query: Description
    :return: Description
    :rtype: str
    """
    return "weather in Kolkata is cold"

if __name__ == "__main__":
    mcp.run(
    transport="streamable-http",
    host="127.0.0.1",
    port=8002,
)
