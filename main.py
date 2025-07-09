"""
A MCP server that uses the dfhack_client_python package to connect to a locally running Dwarf Fortress game through DFHack's RPC connection.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from dfhack_client_python.dfhack_remote import connect, close
from dfhack_client_python.dfhack import GetVersion, GetDFVersion, GetUnitList, GetWorldInfo, GetViewInfo
from dfhack_client_python.py_export.BasicApi_pb2 import GetWorldInfoOut

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Connect to DFHack on startup and close the connection when the server shuts down"""
    await connect()
    #TODO: Need to prefetch and cache static data like materials, units, etc.
    yield
    await close()

app = FastAPI(
    lifespan=lifespan
)

@app.get("/get-versions", operation_id="get_versions")
async def get_versions():
    """Get the DFHack and Dwarf Fortress versions for connected server"""
    dfhack_version = (await GetVersion()).value
    dwarf_fortress_version = (await GetDFVersion()).value
    return {
        "dfhackVersion": dfhack_version,
        "dwarfFortressVersion": dwarf_fortress_version
    }

@app.get("/get-world-info", operation_id="get_world_info")
async def get_world_info():
    """Get the world specific info for the currently running game"""
    world_info = await GetWorldInfo()
    details = {}
    if world_info.mode == GetWorldInfoOut.Mode.MODE_DWARF:
        details = {
            "civId": world_info.civ_id,
            "siteId": world_info.site_id,
            "groupId": world_info.group_id,
            "raceId": world_info.race_id
        }

    return {
        "worldName": {
            "languageId": world_info.world_name.language_id,
            "firstName": world_info.world_name.first_name,
            "lastName": world_info.world_name.last_name,
            "nickname": world_info.world_name.nickname,
            "englishName": world_info.world_name.english_name
        },
        "mode": GetWorldInfoOut.Mode.Name(world_info.mode),
        "details": details
    }

@app.get("/get-view-info", operation_id="get_view_info")
async def get_view_info():
    """Get the view info for the currently running game"""
    view_info = await GetViewInfo()
    return {
        "viewInfo": view_info
    }

@app.get("/get-unit-list", operation_id="get_unit_list")
async def get_unit_list():
    """Get the list of units in the currently running game"""
    return { "message": "Units: " + str(len((await GetUnitList()).creature_list)) }

# TODO:
# - RunCommand (Run a DFHack command)
# - GetBlockList (Get MapBlock info for all blocks in a 3d volume)
# - ListUnits (Get BasicUnitInfo on a specific list of units or a list of matching units based on filters)
# - GetPlantList? (Not sure how usefull this is as the PlatDef type only gives a location and an index ...)
# - GetUnitListInside (GetListOf)
# - GetViewInfo (very useful for determining what the player is currently seeing)
# - PassKeyboardEvent (for perfomring shortcuts for the player maybe. Might be better with RunCommmand)
# - SetPauseState
# - GetPauseState
# - GetReports (Useful but returns a lot of info, might need a way to cache and filter the data)

mcp = FastApiMCP(
    app,
    name="Dwarf Fortress MCP Server",
    description="A MCP server that uses the dfhack_client_python package to connect to a locally running Dwarf Fortress game through DFHack's RPC connection."
)
mcp.mount()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
