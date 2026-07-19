# MCP Bridge Controller Architecture

This implementation creates an architecture where Qoder sees only one MCP server that acts as a bridge to individual MCP servers.

## Architecture Overview

1. **Single Bridge MCP Server**: Qoder sees only one MCP server (`mcp-bridge`) in the configuration
2. **Individual MCP Servers**: Stored separately as JSON configuration files
3. **Dynamic Loading**: Bridge controller loads individual servers when needed

## Directory Structure

```
C:\Users\JJ\AppData\Local\Programs\Qoder\tools\
├── mcp.json                  # Main MCP configuration with only the bridge server
├── individual_mcp_servers\   # Individual MCP server configurations
│   ├── web-search.json
│   ├── repomix.json
│   ├── github.json
│   ├── sequential-thinking.json
│   ├── context7.json
│   ├── postgres.json
│   ├── mcp-json-tool.json
│   ├── filesystem.json
│   ├── memory.json
│   └── shell.json
└── bridge_controller\        # Bridge controller implementation
    ├── bridge_controller.js
    ├── bridge_mcp_server.js
    ├── demo_tool.js
    └── package.json
```

## How It Works

1. Qoder loads only the `mcp-bridge` server from the main configuration
2. When an MCP tool is needed, Qoder communicates with the bridge controller
3. The bridge controller dynamically loads the appropriate individual MCP server
4. The individual server is spawned as a separate process
5. Communication is forwarded between Qoder and the individual server

## Benefits

- **Clean Interface**: Qoder sees only one MCP server
- **Modularity**: Individual servers are stored and managed separately
- **Scalability**: Easy to add new MCP servers without changing main configuration
- **Resource Efficiency**: Servers are loaded only when needed
- **Maintainability**: Each server configuration is in its own file

## Usage

To use this architecture:

1. Replace your main `mcp.json` file with the one that only contains the `mcp-bridge` server
2. Ensure all individual MCP server configurations are in the `individual_mcp_servers` directory
3. The bridge controller will automatically make all servers available to Qoder