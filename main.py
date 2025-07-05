"""
A MCP server that uses the dfhack_client_python package to connect to a locally running Dwarf Fortress game through DFHack's RPC connection.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from dfhack_client_python.dfhack_remote import connect, close
from dfhack_client_python.dfhack import GetVersion, GetUnitList

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Connect to DFHack on startup and close the connection when the server shuts down"""
    await connect()
    yield
    await close()

app = FastAPI(
    lifespan=lifespan
)

@app.get("/get_dfhack_version", operation_id="get_dfhack_version")
async def get_dfhack_version():
    """Get the version of DFHack"""
    return { "message": (await GetVersion()).value }

@app.get("/get_unit_list", operation_id="get_unit_list")
async def get_unit_list():
    """Get the list of units in the currently running Dwarf Fortress game"""
    return { "message": "Units: " + str(len((await GetUnitList()).creature_list)) }

mcp = FastApiMCP(
    app,
    name="Dwarf Fortress MCP Server",
    description="A MCP server that uses the dfhack_client_python package to connect to a locally running Dwarf Fortress game through DFHack's RPC connection."
)
mcp.mount()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
