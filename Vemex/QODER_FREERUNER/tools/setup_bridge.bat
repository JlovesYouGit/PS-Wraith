@echo off
echo Setting up MCP Bridge Controller Architecture
echo ==========================================
echo.

echo Verifying architecture setup...
node "C:\Users\JJ\AppData\Local\Programs\Qoder\tools\setup_bridge_architecture.js"

echo.
echo Testing bridge controller...
node "C:\Users\JJ\AppData\Local\Programs\Qoder\tools\bridge_controller\test_bridge.js"

echo.
echo Setup complete! 
echo.
echo To use this architecture:
echo 1. Make sure your Qoder mcp.json points to the bridge controller
echo 2. Restart Qoder
echo 3. All MCP servers will be available through the bridge
echo.
pause