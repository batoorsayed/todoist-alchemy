# Todoist Alchemy MCP

Todoist Alchemy is an AI-powered task organization system that leverages Claude and the Model Context Protocol (MCP) to transform unstructured Todoist tasks into well-organized, actionable items.

## Features

- Cleans up task names for clarity and consistency
- Adds short, informative descriptions
- Estimates required work hours
- Assigns appropriate priority levels
- Adds relevant labels for time-block categorization
- Associates tasks with appropriate projects and sections
- Breaks down complex tasks into subtasks when necessary

## Setup

### Prerequisites

- Python 3.8+
- Claude Desktop app
- Todoist account and API token

### Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/todoist-alchemy-mcp.git
cd todoist-alchemy-mcp
```

2. Install dependencies:
```
pip install mcp todoist-api-python python-dotenv
```
3. Set up environment variables:
```
cp .env.example .env
```

Then edit the `.env` file and add your Todoist API token.

4. Configure Claude Desktop:
- Open or create `~/Library/Application Support/Claude/claude_desktop_config.json`
- Add the following configuration (replace paths as needed):
  ```json
  {
    "mcpServers": {
      "todoist-alchemy": {
        "command": "python3",
        "args": [
          "/path/to/todoist-alchemy-mcp/src/server.py"
        ],
        "env": {
          "TODOIST_API_TOKEN": "your_todoist_api_token_here"
        }
      }
    }
  }
  ```

5. Restart Claude Desktop

## Usage

1. Open Claude Desktop
2. Look for the hammer icon at the bottom of the chat window, which indicates MCP tools are available
3. Ask Claude to organize your Todoist tasks
4. Claude will use the tools to fetch, process, and update your tasks

## Security Notes

- Your Todoist API token is stored locally in the Claude Desktop config file and/or .env file
- The token is never transmitted beyond the necessary API calls to Todoist
- No data is sent to external servers other than the official Todoist API

## License

MIT