from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import signal
import sys
import traceback
import time

# NBA API related imports (assuming they are in requirements.txt)
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.static import players

# Graceful shutdown
def signal_handler(sig, frame):
    print("Shutting down SSE MCP server gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

print(f"SSE MCP Server: Current working directory: {os.getcwd()}", file=sys.stderr)

# Initialize FastMCP server
mcp = FastMCP(name="nba_sse_mcp_server")

# --- Tool Definitions ---

# 1) Live ScoreBoard Tool
class LiveScoreBoardInput(BaseModel):
    dummy_param: Optional[str] = Field(default="", description="Not used by this tool.")

@mcp.tool()
def nba_live_scoreboard(dummy_param: Optional[str] = "") -> Dict[str, Any]:
    """Fetch today's NBA scoreboard (live or latest).
    Provides game IDs, start times, scores, period information, and broadcast details.
    """
    try:
        sb = scoreboard.ScoreBoard()
        return sb.get_dict()
    except Exception as e:
        print(f"Error in nba_live_scoreboard: {e}", file=sys.stderr)
        return {"error": str(e)}

# 2) List All Active Players
class ListActivePlayersInput(BaseModel):
    dummy: Optional[str] = Field(default="", description="Not used by this tool.")

@mcp.tool()
def nba_list_active_players(dummy: Optional[str] = "") -> List[Dict[str, Any]]:
    """Return a list of all currently active NBA players with their IDs and names."""
    try:
        all_active = players.get_active_players()
        return all_active
    except Exception as e:
        print(f"Error in nba_list_active_players: {e}", file=sys.stderr)
        return [{"error": str(e)}]

# --- Main execution block ---
if __name__ == "__main__":
    try:
        port_to_use = int(os.environ.get("PORT", 8000)) # Railway provides PORT
        host_to_use = "0.0.0.0" # Listen on all interfaces

        print(f"[SERVER_SCRIPT] Starting NBA SSE MCP server at path /sse (host/port should be handled by environment or defaults for SSE transport)", file=sys.stderr)
        
        # Ensure FastMCP version is compatible with this way of running SSE
        print(f"[SERVER_SCRIPT] Attempting to run mcp.run() for SSE...", file=sys.stderr)
        mcp.run(
            transport="sse",
            # host=host_to_use, # Removed based on TypeError
            # port=port_to_use, # Removed based on TypeError
            path="/sse" # Standard path for SSE MCP endpoint
        )
        # If mcp.run() is blocking and successful, this line won't be reached until shutdown.
    except Exception as e:
        print(f"Critical error starting SSE MCP server: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        time.sleep(5) # Keep alive for logs on crash
        sys.exit(1) 