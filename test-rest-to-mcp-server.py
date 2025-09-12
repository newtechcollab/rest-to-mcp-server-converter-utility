import asyncio

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.mcp import MCPTools, MultiMCPTools, StreamableHTTPClientParams

# This is the URL of the MCP server we want to use.
server_url = "http://localhost:5555/mcp"
#server_url = "http://127.0.0.1:2222/mcp"


async def run_agent(message: str) -> None:

    # Initialize the MCP tools
    server_params = StreamableHTTPClientParams(
        url=server_url,
        headers={
            "user-agent": "gomez",
            "x-operation": "123",
            "X-operation": "value",
            "x_operation": "1234",
            "X_operation": "value22",
            "Xoperation": "value2",
        },
    )
    mcp_tools = MCPTools(server_params=server_params, transport="streamable-http")
    #mcp_tools = MCPTools(transport="streamable-http", url=server_url)

    # Connect to the MCP server
    await mcp_tools.connect()

    # Initialize the Agent
    agent = Agent(
        model=Gemini(id="gemini-2.5-flash"),
        tools=[mcp_tools],
        markdown=True,
        add_history_to_messages=True,
    )

    # Run the agent
    await agent.aprint_response(message=message, stream=True, markdown=True)

    # Close the MCP connection
    await mcp_tools.close()


async def execute():
    while True:
        print("What do you want to ask? If you are finished and want to exit, just type END")
        line = input()
        print(f"You have entered {line}")
        if (line == "END"):
            break
        await run_agent(line)
if __name__ == "__main__":
    #asyncio.run(run_agent("Get the list of planets"))
    asyncio.run(execute())
