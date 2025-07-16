# Revit MCP

A Model Context Protocol (MCP) server that provides **real screen capture, keyboard automation, and Revit journal access** capabilities for Revit and other applications, built using the XMCP framework.

This project is the result of the initial ideas and design documents, culminating in a functional `revit-mcp` implementation.

## ✅ Current Status

- **Framework**: ✅ Successfully implemented using XMCP
- **Screen Capture**: ✅ Real screen capture using PowerShell and Windows .NET APIs
- **Keyboard Automation**: ✅ Real keyboard automation using PowerShell SendKeys
- **Revit Journals**: ✅ Access to Revit journal files for the current session.
- **Server**: ✅ Running correctly with STDIO transport
- **Production Ready**: ✅ Fully functional for Cursor and Claude Desktop

## 🛠️ Available Tools

### 1. `capture_screen`
Captures the current screen or a specific region and returns as base64 image using Windows .NET APIs.

**Parameters:**
- `region` (optional): Object with x, y, width, height for specific region capture
- `format` (optional): "png" or "jpg" (default: "png")
- `quality` (optional): 1-100 for JPG quality (default: 90)
- `resize` (optional): Object with width/height for resizing

**Example Usage:**
```json
{
  "region": {"x": 100, "y": 100, "width": 800, "height": 600},
  "format": "png",
  "quality": 90
}
```

### 2. `send_keys`
Sends keyboard input to the active window using Windows SendKeys with support for key combinations and special keys.

**Parameters:**
- `keys` (required): Keys to send
  - Text: `"Hello World"`
  - Shortcuts: `"ctrl+s"`, `"alt+tab"`
  - Special keys: `"[enter]"`, `"[tab]"`
- `delay` (optional): Delay before sending keys in milliseconds (default: 100)
- `simultaneous` (optional): Press key combinations simultaneously (default: true)

**Example Usage:**
```json
{
  "keys": "ctrl+s",
  "delay": 100,
  "simultaneous": true
}
```

### 3. `revit_journals`
Access Revit journal files from the current session only. Provides secure, read-only access to Revit's journal files for debugging and monitoring purposes.

**Parameters:**
- `action` (required): 'list', 'read_latest', 'read_file', or 'tail'
- `filename` (optional): Specific journal filename to read
- `lines` (optional): Number of lines to read from the end (for tail action)

**Example Usage:**
```json
{
  "action": "tail",
  "lines": 100
}
```

## 🚀 Getting Started

### Installation

```bash
cd revit-mcp
npm install
npm run build
```

### Running the Server

#### STDIO Transport (for Cursor/Claude Desktop)
```bash
npm run start-stdio
# or
node dist/stdio.js
```

#### HTTP Transport (for testing)
```bash
npm run start-http
# Server will run on http://localhost:3002
```

## 🎯 Configuration

### Cursor Configuration

1. **Option 1: Use the provided config file**
   ```bash
   # Copy the provided cursor-mcp-config.json to your Cursor settings
   cp revit-mcp/cursor-mcp-config.json ~/.cursor/mcp-config.json
   ```

2. **Option 2: Manual configuration**
   Add to your Cursor MCP configuration:
   ```json
   {
     "mcpServers": {
       "revit-screen-capture": {
         "command": "node",
         "args": ["C:/Users/leobr/Workspace/challenges/mcp/revit-mcp/dist/stdio.js"],
         "env": {
           "NODE_ENV": "production"
         }
       }
     }
   }
   ```

## 🏗️ Architecture

Built using modern MCP patterns with **real functionality**:

- **XMCP Framework**: Latest MCP development framework
- **TypeScript**: Full type safety and IDE support
- **Zod Validation**: Runtime parameter validation
- **PowerShell Integration**: Real Windows automation without native compilation
- **Windows .NET APIs**: Native screen capture and keyboard automation
- **Modular Design**: Isolated, reusable tool components
- **Multiple Transports**: STDIO for Cursor/Claude, HTTP for testing

## 🔒 Security & Requirements

- **Windows Only**: Uses PowerShell and Windows .NET APIs
- **PowerShell Required**: Execution policy must allow script execution
- **No Native Compilation**: No need for Visual Studio or Windows SDK
- **Permissions**: Requires normal user permissions (no admin needed)
