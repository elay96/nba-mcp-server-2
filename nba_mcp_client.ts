import EasyMCP, { Context } from "easy-mcp";
import { Tool } from "easy-mcp/experimental/decorators";

// NBA Stats API base URL
const NBA_STATS_BASE_URL = "https://stats.nba.com/stats";

// Common headers for NBA Stats API calls
// stats.nba.com can be sensitive to headers. These are common ones.
const NBA_API_HEADERS = {
  "Host": "stats.nba.com",
  "Connection": "keep-alive",
  "Cache-Control": "max-age=0",
  "Upgrade-Insecure-Requests": "1",
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
  "Accept": "application/json, text/plain, */*",
  "Accept-Encoding": "gzip, deflate, br",
  "Accept-Language": "en-US,en;q=0.9",
  "Referer": "https://www.nba.com/",
  "Origin": "https://www.nba.com/"
};

class NbaMcpClient extends EasyMCP {
  constructor() {
    const port = process.env.PORT ? parseInt(process.env.PORT, 10) : 3000; // Default to 3000 if PORT not set
    super({ name: "nba-mcp-client", version: "0.1.0", port });
  }

  @Tool({
    description: "Fetches a list of all NBA players for a given season.",
    parameters: [
      { name: "season", type: "string", description: "The season to fetch players for (e.g., '2023-24')", required: true },
      { name: "isOnlyCurrentSeason", type: "boolean", description: "Flag for current season only (0 for all, 1 for current)", required: false, default: false }
    ],
    optionals: ["isOnlyCurrentSeason"]
  })
  async getPlayers(season: string, isOnlyCurrentSeason: boolean = false, context?: Context) {
    const leagueId = "00"; // NBA
    const currentSeasonFlag = isOnlyCurrentSeason ? "1" : "0";
    const endpoint = `${NBA_STATS_BASE_URL}/commonallplayers?LeagueID=${leagueId}&Season=${season}&IsOnlyCurrentSeason=${currentSeasonFlag}`;

    context?.info(`Fetching players from NBA API: ${endpoint}`);
    try {
      const response = await fetch(endpoint, { headers: NBA_API_HEADERS });
      if (!response.ok) {
        throw new Error(`NBA API request failed with status ${response.status}: ${await response.text()}`);
      }
      return await response.json();
    } catch (error: any) {
      context?.error(`Error fetching players: ${error.message}`);
      throw error;
    }
  }

  @Tool({
    description: "Fetches a list of all NBA teams.",
  })
  async getTeams(context?: Context) {
    const leagueId = "00"; // NBA
    const endpoint = `${NBA_STATS_BASE_URL}/commonteamyears?LeagueID=${leagueId}`;
    
    context?.info(`Fetching teams from NBA API: ${endpoint}`);
    try {
      const response = await fetch(endpoint, { headers: NBA_API_HEADERS });
      if (!response.ok) {
        throw new Error(`NBA API request failed with status ${response.status}: ${await response.text()}`);
      }
      return await response.json();
    } catch (error: any) {
      context?.error(`Error fetching teams: ${error.message}`);
      throw error;
    }
  }

  @Tool({
    description: "Fetches information for a specific player.",
    parameters: [
      { name: "playerId", type: "number", description: "The ID of the player (e.g., 2544 for LeBron James)", required: true },
    ],
  })
  async getPlayerInfo(playerId: number, context?: Context) {
    const endpoint = `${NBA_STATS_BASE_URL}/commonplayerinfo?PlayerID=${playerId}`;
    
    context?.info(`Fetching player info for PlayerID ${playerId} from NBA API: ${endpoint}`);
    try {
      const response = await fetch(endpoint, { headers: NBA_API_HEADERS });
      if (!response.ok) {
        throw new Error(`NBA API request failed with status ${response.status}: ${await response.text()}`);
      }
      return await response.json();
    } catch (error: any) {
      context?.error(`Error fetching player info: ${error.message}`);
      throw error;
    }
  }
  
  @Tool({
    description: "Fetches play-by-play data for a specific game.",
    parameters: [
      { name: "gameId", type: "string", description: "The 10-digit ID of the game (e.g., '0022300001')", required: true },
    ],
  })
  async getGamePlayByPlay(gameId: string, context?: Context) {
    const endpoint = `${NBA_STATS_BASE_URL}/playbyplayv2?GameID=${gameId}&StartPeriod=0&EndPeriod=14`; // EndPeriod 14 covers potential overtimes

    context?.info(`Fetching play-by-play for GameID ${gameId} from NBA API: ${endpoint}`);
    try {
      const response = await fetch(endpoint, { headers: NBA_API_HEADERS });
      if (!response.ok) {
        throw new Error(`NBA API request failed with status ${response.status}: ${await response.text()}`);
      }
      return await response.json();
    } catch (error: any) {
      context?.error(`Error fetching play-by-play data: ${error.message}`);
      throw error;
    }
  }

  @Tool({
    description: "Fetches the roster for a specific team and season.",
    parameters: [
        { name: "teamId", type: "number", description: "The ID of the team", required: true },
        { name: "season", type: "string", description: "The season (e.g., '2023-24')", required: false }
    ],
    optionals: ["season"]
  })
  async getTeamRoster(teamId: number, season?: string, context?: Context) {
    const currentSeason = season || "2023-24"; // Default to a recent season
    const endpoint = `${NBA_STATS_BASE_URL}/commonteamroster?TeamID=${teamId}&Season=${currentSeason}`;

    context?.info(`Fetching team roster for TeamID ${teamId}, Season ${currentSeason} from NBA API: ${endpoint}`);
    try {
      const response = await fetch(endpoint, { headers: NBA_API_HEADERS });
      if (!response.ok) {
        throw new Error(`NBA API request failed with status ${response.status}: ${await response.text()}`);
      }
      return await response.json();
    } catch (error: any) {
      context?.error(`Error fetching team roster: ${error.message}`);
      throw error;
    }
  }
  
  @Tool({
    description: "Finds the most recent game ID for a team in a given season and season type.",
    parameters: [
        { name: "teamId", type: "number", description: "The ID of the team", required: true },
        { name: "season", type: "string", description: "The season (e.g., '2023-24')", required: false },
        { name: "seasonType", type: "string", description: "Season type (e.g., 'Regular Season', 'Playoffs')", required: false }
    ],
    optionals: ["season", "seasonType"]
  })
  async findRecentGameId(teamId: number, season?: string, seasonType?: string, context?: Context) {
    const currentSeason = season || "2023-24"; // Default season if not provided
    const type = seasonType || "Regular Season"; // Default season type
    const leagueId = "00"; // NBA

    const endpoint = `${NBA_STATS_BASE_URL}/leaguegamefinder?TeamID=${teamId}&Season=${currentSeason}&SeasonType=${encodeURIComponent(type)}&LeagueID=${leagueId}`;

    context?.info(`Finding recent game ID for TeamID ${teamId} from NBA API: ${endpoint}`);
    try {
      const response = await fetch(endpoint, { headers: NBA_API_HEADERS });
      if (!response.ok) {
        throw new Error(`NBA API request failed with status ${response.status} ${response.statusText}: ${await response.text()}`);
      }
      const data = await response.json();
      
      if (data.resultSets && data.resultSets.length > 0) {
        const gameFinderResultsSet = data.resultSets.find((rs: any) => rs.name === "LeagueGameFinderResults");
        if (gameFinderResultsSet && gameFinderResultsSet.rowSet && gameFinderResultsSet.rowSet.length > 0) {
            const headers = gameFinderResultsSet.headers;
            const gameIdIndex = headers.indexOf("GAME_ID");
            const gameDateIndex = headers.indexOf("GAME_DATE");

            if (gameIdIndex === -1 || gameDateIndex === -1) {
              return { error: "GAME_ID or GAME_DATE not found in results headers", rawData: data };
            }

            // Sort games by date descending to get the most recent one first
            const sortedGames = [...gameFinderResultsSet.rowSet].sort((a: any[], b: any[]) => {
                const dateA = new Date(a[gameDateIndex]).getTime();
                const dateB = new Date(b[gameDateIndex]).getTime();
                return dateB - dateA;
            });
            
            const mostRecentGame = sortedGames[0];
            const gameDetails: { [key: string]: any } = {};
            headers.forEach((header: string, index: number) => {
                gameDetails[header] = mostRecentGame[index];
            });

            return { 
                game_id: mostRecentGame[gameIdIndex], 
                game_details: gameDetails 
            };
        }
      }
      return { error: "No games found or unexpected data structure", rawData: data };
    } catch (error: any) {
      context?.error(`Error finding recent game ID: ${error.message}`);
      throw error;
    }
  }
}

// Create and serve the MCP client
const mcp = new NbaMcpClient();

mcp.serve()
  .then(() => {
    console.log(`${mcp.name} (v${mcp.config.version}) is now serving!`);
    console.log("Available tools:");
    if (mcp.tools && mcp.tools.length > 0) {
      mcp.tools.forEach((tool: { name?: string, description?: string, constructor?: Function }) => {
        const toolName = tool.name || (typeof tool.constructor === 'function' ? tool.constructor.name : 'UnknownTool');
        const toolDescription = (tool as any).description || 'No description available.';
        console.log(`- ${toolName}: ${toolDescription}`);
      });
    } else {
        console.log("Inspect the 'mcp' object or EasyMCP documentation for how to list registered tools dynamically.");
        console.log("- getPlayers: Fetches a list of all NBA players for a given season.");
        console.log("- getTeams: Fetches a list of all NBA teams.");
        console.log("- getPlayerInfo: Fetches information for a specific player.");
        console.log("- getGamePlayByPlay: Fetches play-by-play data for a specific game.");
        console.log("- getTeamRoster: Fetches the roster for a specific team and season.");
        console.log("- findRecentGameId: Finds the most recent game ID for a team in a given season and season type.");
    }
  })
  .catch((error: Error) => {
    console.error("Failed to start NBA MCP Client:", error);
  });

// Note: Ensure you have 'easy-mcp' installed in your project.
// You might need to run 'npm install easy-mcp' or 'yarn add easy-mcp' or 'bun install easy-mcp'.
// For Node.js environments older than v18, you might need to use a polyfill for fetch (e.g., 'node-fetch').
// The import paths used are "easy-mcp" and "easy-mcp/experimental/decorators".
// Adjust if your 'easy-mcp' installation exposes modules differently. 