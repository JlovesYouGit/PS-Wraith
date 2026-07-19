const chalk = require('chalk');
const { startServer } = require('../mcp/mcp-server');

module.exports = {
  command: 'mcp-server',
  description: 'Start the BMAD MCP (Modular Capability Platform) server',
  options: [['-p, --port <port>', 'Port to run the MCP server on (default: 3174)']],
  action: async (options) => {
    try {
      console.log(chalk.blue('🚀 Starting BMAD MCP Server...'));

      // Set port from options or environment variable
      if (options.port) {
        process.env.BMAD_MCP_PORT = options.port;
      }

      // Start the MCP server
      const server = startServer();

      console.log(chalk.green('✅ BMAD MCP Server started successfully!'));
      console.log(chalk.cyan('\nAvailable endpoints:'));
      console.log(chalk.dim('  GET  /              - Health check'));
      console.log(chalk.dim('  GET  /tools         - List available tools'));
      console.log(chalk.dim('  POST /execute       - Execute a tool'));
      console.log(chalk.yellow('\nPress Ctrl+C to stop the server'));

      // Keep the process alive
      process.on('SIGINT', () => {
        console.log(chalk.yellow('\n🛑 Stopping MCP server...'));
        server.close(() => {
          console.log(chalk.green('✅ MCP server stopped'));
          process.exit(0);
        });
      });
    } catch (error) {
      console.error(chalk.red('Failed to start MCP server:'), error.message);
      process.exit(1);
    }
  },
};
