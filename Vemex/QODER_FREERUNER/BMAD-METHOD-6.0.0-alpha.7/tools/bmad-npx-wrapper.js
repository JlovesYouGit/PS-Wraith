#!/usr/bin/env node

/**
 * BMad Method CLI - Direct execution wrapper for npx
 * This file ensures proper execution when run via npx from GitHub or npm registry
 */

const { execSync } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');

// Check if we're running in an npx temporary directory
const isNpxExecution = __dirname.includes('_npx') || __dirname.includes('.npm');

// Check if MCP server command is requested
const args = process.argv.slice(2);
const isMcpServer = args.includes('mcp-server') || args.includes('mcp');

if (isMcpServer) {
  // Running MCP server - directly execute the MCP server
  const mcpServerPath = path.join(__dirname, 'cli', 'mcp', 'mcp-server.js');

  if (!fs.existsSync(mcpServerPath)) {
    console.error('Error: Could not find mcp-server.js at', mcpServerPath);
    process.exit(1);
  }

  try {
    // Execute MCP server
    execSync(`node "${mcpServerPath}"`, {
      stdio: 'inherit',
      cwd: process.cwd(),
    });
  } catch (error) {
    process.exit(error.status || 1);
  }
} else if (isNpxExecution) {
  // Running via npx - spawn child process to preserve user's working directory
  const bmadCliPath = path.join(__dirname, 'cli', 'bmad-cli.js');

  if (!fs.existsSync(bmadCliPath)) {
    console.error('Error: Could not find bmad-cli.js at', bmadCliPath);
    console.error('Current directory:', __dirname);
    process.exit(1);
  }

  try {
    // Execute CLI from user's working directory (process.cwd()), not npm cache
    execSync(`node "${bmadCliPath}" ${args.join(' ')}`, {
      stdio: 'inherit',
      cwd: process.cwd(), // This preserves the user's working directory
    });
  } catch (error) {
    process.exit(error.status || 1);
  }
} else {
  // Local execution - use require
  require('./cli/bmad-cli.js');
}
