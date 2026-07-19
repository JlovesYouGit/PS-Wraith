# Qoder MCP Integration for BMAD

## Overview

The BMAD-METHOD now includes seamless integration with Qoder IDE through the Modular Capability Platform (MCP). This integration enhances the development experience by providing advanced capabilities through modular tools and services.

## Features

### MCP-Enhanced Agents

Qoder users get access to specialized agent variations with MCP integration:

1. **PM-Technical** - Product Manager with Technical Focus
2. **Architect-Advanced** - Advanced Solution Architect with MCP Integration
3. **Dev-MCP** - Developer with Full MCP Capabilities
4. **Qoder Developer** - Specialized developer agent for Qoder IDE

### MCP Tools

The integration provides several powerful tools:

- **Code Analyzer** - Real-time code analysis and suggestions
- **Workflow Orchestrator** - Enhanced workflow execution with MCP
- **Debug Assistant** - MCP-based debugging assistance
- **Test Generator** - Automated test generation and execution
- **Performance Analyzer** - Code performance analysis and optimization

### Qoder-Specific Capabilities

- **Real-time Code Analysis** - Analyze code as you write with MCP-powered insights
- **Automated Debugging** - Use MCP tools to identify and fix issues automatically
- **Intelligent Code Generation** - Generate code based on requirements with MCP validation
- **Performance Optimization** - Optimize code performance using MCP analysis tools
- **Test Automation** - Automatically generate and run tests with MCP

## Installation

When installing the BMAD-METHOD with Qoder IDE selected, the MCP integration is automatically enabled. The installation process:

1. Adds Qoder-specific configuration to the BMM module
2. Creates MCP-enhanced agent variations
3. Sets up MCP server configuration
4. Registers MCP tools with the system

## Configuration

The integration can be configured through the installation process:

```
? Enable Qoder IDE MCP integration (advanced workflows, enhanced tools)? (Y/n)
? Enable Qoder advanced features (MCP-based workflows, enhanced debugging)? (Y/n)
```

## Usage

### Starting the MCP Server

To start the MCP server manually:

```bash
npx bmad-method mcp-server
# or
npm run bmad:mcp
```

### Using MCP-Enhanced Agents

Once installed, Qoder-enhanced agents will be available in your BMAD installation. These agents provide additional capabilities through MCP integration.

### Executing MCP Tools

MCP tools can be executed through the Qoder IDE interface or programmatically through the MCP server API.

## API Endpoints

The MCP server provides the following endpoints:

- `GET /` - Health check
- `GET /tools` - List available tools
- `POST /execute` - Execute a tool

Example tool execution:

```json
{
  "toolName": "bmad-agent-executor",
  "projectName": "my-project",
  "toolParams": {
    "agentModule": "bmm",
    "agentName": "dev-mcp",
    "userInput": "Generate a React component for a user profile"
  }
}
```

## Development

### Adding New MCP Tools

To add new MCP tools:

1. Create a tool definition in `src/core/mcp/mcp-integration.js`
2. Implement the tool functionality
3. Register the tool with the MCP server

### Extending Qoder Integration

To extend the Qoder integration:

1. Modify `src/modules/bmm/_module-installer/platform-specifics/qoder.js`
2. Add new agent variations or workflow enhancements
3. Update the Qoder IDE handler in `tools/cli/installers/lib/ide/qoder.js`

## Troubleshooting

### MCP Server Not Starting

Ensure that:

- Port 3174 (or your configured port) is available
- Node.js version 20+ is installed
- All dependencies are installed (`npm install`)

### Tools Not Available

If MCP tools are not appearing:

- Verify the MCP server is running
- Check that tools are properly registered
- Ensure the Qoder IDE configuration is correct

## Future Enhancements

Planned enhancements for the Qoder MCP integration:

1. **Enhanced Debugging Workflows** - More sophisticated debugging assistance
2. **AI-Powered Refactoring** - Intelligent code refactoring suggestions
3. **Performance Profiling** - Detailed performance analysis and optimization
4. **Security Analysis** - Automated security vulnerability detection
5. **Code Review Automation** - AI-powered code review with MCP validation

## Support

For issues with the Qoder MCP integration, please:

1. Check the [BMAD Discord](https://discord.gg/gk8jAdXWmj) community
2. File issues on the [GitHub repository](https://github.com/bmad-code-org/BMAD-METHOD/issues)
3. Consult the [BMAD Documentation](./README.md)
