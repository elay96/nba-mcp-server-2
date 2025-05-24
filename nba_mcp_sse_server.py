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
    print("[SERVER_SCRIPT] Main execution block started.", file=sys.stderr)
    try:
        port_to_use = int(os.environ.get("PORT", 8000)) # Railway provides PORT
        host_to_use = "0.0.0.0" # Listen on all interfaces
        mcp_path = "/sse" # Define the desired MCP path for SSE

        print(f"[SERVER_SCRIPT] Configuring FastMCP as ASGI app for Uvicorn.", file=sys.stderr)
        print(f"[SERVER_SCRIPT] Target: {host_to_use}:{port_to_use}, MCP Path: {mcp_path}", file=sys.stderr)
        
        # Get the ASGI application from FastMCP, specifying the path for MCP
        mcp_asgi_app = mcp.asgi_app(path=mcp_path)
        print(f"[SERVER_SCRIPT] ASGI app created from FastMCP.", file=sys.stderr)

        # Import uvicorn here, as it's only needed for running.
        import uvicorn
        print(f"[SERVER_SCRIPT] Uvicorn imported. Attempting to start Uvicorn...", file=sys.stderr)

        uvicorn.run(
            mcp_asgi_app,
            host=host_to_use, 
            port=port_to_use,
            log_level="info"
        )
        # If uvicorn.run() exits, it means the server was stopped or crashed.
        print("[SERVER_SCRIPT] Uvicorn run command finished.", file=sys.stderr)

    except Exception as e:
        print(f"[SERVER_SCRIPT_CRITICAL_ERROR] Critical error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        time.sleep(15) # Keep alive longer for logs on crash
        sys.exit(1)
    
    print("[SERVER_SCRIPT] Main execution block finished normally (e.g., Uvicorn stopped gracefully).", file=sys.stderr)
    sys.exit(0) 