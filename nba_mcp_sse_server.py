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
    print("Shutting down SSE MCP server gracefully...", file=sys.stderr)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

print(f"SSE MCP Server: Current working directory: {os.getcwd()}", file=sys.stderr)

# Initialize FastMCP server
# We initialize mcp globally so tools can be registered,
# but the actual ASGI app configuration happens in __main__
try:
    mcp = FastMCP(name="nba_sse_mcp_server")
    print(f"[SERVER_SCRIPT] Initialized FastMCP with name: {mcp.name}", file=sys.stderr)
except Exception as e:
    print(f"[SERVER_SCRIPT_CRITICAL_ERROR] Failed to initialize FastMCP: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)


# --- Tool Definitions ---

# 1) Live ScoreBoard Tool
class LiveScoreBoardInput(BaseModel):
    dummy_param: Optional[str] = Field(default="", description="Not used by this tool.")

@mcp.tool()
def nba_live_scoreboard(dummy_param: Optional[str] = "") -> Dict[str, Any]:
    """Fetch today's NBA scoreboard (live or latest).
    Provides game IDs, start times, scores, period information, and broadcast details.
    """
    print("[TOOL_LOG] nba_live_scoreboard called", file=sys.stderr)
    try:
        sb = scoreboard.ScoreBoard()
        data = sb.get_dict()
        print("[TOOL_LOG] nba_live_scoreboard success", file=sys.stderr)
        return data
    except Exception as e:
        print(f"[TOOL_ERROR] Error in nba_live_scoreboard: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return {"error": str(e), "details": traceback.format_exc()}

# 2) List All Active Players
class ListActivePlayersInput(BaseModel):
    dummy: Optional[str] = Field(default="", description="Not used by this tool.")

@mcp.tool()
def nba_list_active_players(dummy: Optional[str] = "") -> List[Dict[str, Any]]:
    """Return a list of all currently active NBA players with their IDs and names."""
    print("[TOOL_LOG] nba_list_active_players called", file=sys.stderr)
    try:
        all_active = players.get_active_players()
        print("[TOOL_LOG] nba_list_active_players success", file=sys.stderr)
        return all_active
    except Exception as e:
        print(f"[TOOL_ERROR] Error in nba_list_active_players: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return [{"error": str(e), "details": traceback.format_exc()}]

# --- Main execution block ---
if __name__ == "__main__":
    print("[SERVER_SCRIPT] Main execution block started.", file=sys.stderr)
    
    mcp_asgi_app = None # Initialize to None

    try:
        # Configuration
        host = os.environ.get("HOST", "0.0.0.0")
        # Railway provides PORT, default to 8080 for local dev if not set.
        port_str = os.environ.get("PORT")
        if port_str is None:
            print("[SERVER_SCRIPT_WARNING] PORT environment variable not set. Defaulting to 8080.", file=sys.stderr)
            port = 8080
        else:
            try:
                port = int(port_str)
            except ValueError:
                print(f"[SERVER_SCRIPT_CRITICAL_ERROR] Invalid PORT value: '{port_str}'. Must be an integer.", file=sys.stderr)
                sys.exit(1)

        mcp_path = "/sse"

        print(f"[SERVER_SCRIPT] Runtime Configuration - Host: {host}, Port: {port}, MCP Path: {mcp_path}", file=sys.stderr)

        # Expose the MCP server as an ASGI application for SSE
        print("[SERVER_SCRIPT] Configuring FastMCP as SSE ASGI app for Uvicorn.", file=sys.stderr)
        
        try:
            # Use sse_app as indicated by the previous error
            mcp_asgi_app = mcp.sse_app(path=mcp_path)
            print(f"[SERVER_SCRIPT] SSE ASGI app created from FastMCP for path: {mcp_path}", file=sys.stderr)
        except AttributeError:
            print("[SERVER_SCRIPT_CRITICAL_ERROR] 'FastMCP' object is missing 'sse_app' attribute. This should not happen after the fix.", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[SERVER_SCRIPT_CRITICAL_ERROR] Error creating SSE ASGI app: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

        if mcp_asgi_app is None:
            print("[SERVER_SCRIPT_CRITICAL_ERROR] mcp_asgi_app was not successfully created. Cannot start Uvicorn.", file=sys.stderr)
            sys.exit(1)
            
        # Import uvicorn here, as it's only needed for running.
        try:
            import uvicorn
            print("[SERVER_SCRIPT] Uvicorn imported successfully.", file=sys.stderr)
        except ImportError:
            print("[SERVER_SCRIPT_CRITICAL_ERROR] Uvicorn is not installed. Please install it: pip install uvicorn", file=sys.stderr)
            sys.exit(1)
            
        print(f"[SERVER_SCRIPT] Attempting to start Uvicorn server on {host}:{port}...", file=sys.stderr)
        
        uvicorn.run(
            mcp_asgi_app,
            host=host,
            port=port,
            log_level="info" 
        )
        
        # If uvicorn.run() exits, it means the server was stopped or crashed.
        print("[SERVER_SCRIPT] Uvicorn run command finished.", file=sys.stderr)

    except SystemExit:
        print("[SERVER_SCRIPT] SystemExit caught. Exiting...", file=sys.stderr)
        # sys.exit calls within signal handlers or error checks will be caught here.
        # Re-raise to ensure the exit code is propagated if it's non-zero.
        raise
    except Exception as e:
        print(f"[SERVER_SCRIPT_CRITICAL_ERROR] Unhandled critical error in main execution block: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        # Adding a small delay for logs to flush, especially in containerized environments
        time.sleep(5) 
        sys.exit(1)
    
    print("[SERVER_SCRIPT] Main execution block finished (e.g., Uvicorn stopped gracefully or an error was handled).", file=sys.stderr)
    sys.exit(0) 