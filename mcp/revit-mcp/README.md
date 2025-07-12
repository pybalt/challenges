# Revit Screen Capture MCP

A Model Context Protocol (MCP) server that provides **real screen capture and keyboard automation** capabilities for Revit and other applications, built using the XMCP framework.

## ✅ Current Status

- **Framework**: ✅ Successfully implemented using XMCP
- **Screen Capture**: ✅ Real screen capture using PowerShell and Windows .NET APIs
- **Keyboard Automation**: ✅ Real keyboard automation using PowerShell SendKeys
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

## 🚀 Getting Started

### Installation

```bash
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
   cp cursor-mcp-config.json ~/.cursor/mcp-config.json
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

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "revit-screen-capture": {
      "command": "node",
      "args": ["C:/Users/leobr/Workspace/challenges/mcp/revit-mcp/dist/stdio.js"]
    }
  }
}
```

## 🎯 Use Cases

### Revit Workflows
- **Model QC**: "Capture the current Revit view and analyze for issues"
- **Documentation**: "Take a screenshot of this floor plan"
- **Automation**: "Save the current model (Ctrl+S) and switch to 3D view"
- **Property Analysis**: "Capture the Properties panel and read the element parameters"

### General Automation
- **Screen Capture**: Capture any application window or region
- **Keyboard Control**: Send any key combination or text input
- **Workflow Automation**: Chain multiple operations together

### Example Conversations

```
User: "What warnings do I have in this model?"
Cursor: [Automatically captures Revit screen using capture_screen tool]
        "I can see 3 warnings in your Properties panel:
        - Room boundary overlap on Level 1
        - Unplaced room tag in Room 101
        - Missing ceiling height parameter"

User: "Save the current file and take a screenshot"
Cursor: [Uses send_keys tool to send Ctrl+S]
        [Uses capture_screen tool to capture the screen]
        "I've saved your file and captured the current view."
```

## 🔧 Development

### Project Structure
```
src/
├── tools/
│   ├── capture-screen.ts    # Real screen capture using PowerShell
│   └── send-keys.ts         # Real keyboard automation using SendKeys
├── package.json             # Dependencies and scripts
├── xmcp.config.ts          # XMCP configuration
└── tsconfig.json           # TypeScript configuration
```

### Building
```bash
npm run build    # Builds both STDIO and HTTP servers
npm run dev      # Development mode with auto-rebuild
```

### Testing Tools
You can test the tools using the HTTP server:

```bash
# Start HTTP server
npm run start-http

# Test capture_screen tool
curl -X POST http://localhost:3002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "capture_screen",
      "arguments": {"format": "png"}
    }
  }'

# Test send_keys tool  
curl -X POST http://localhost:3002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call", 
    "params": {
      "name": "send_keys",
      "arguments": {"keys": "ctrl+s"}
    }
  }'
```

## 🔮 Roadmap

### Phase 1: Core Framework ✅
- [x] XMCP-based MCP server
- [x] Basic tool structure
- [x] STDIO and HTTP transports
- [x] Tool parameter validation

### Phase 2: Screen Capture ✅
- [x] PowerShell-based screen capture
- [x] Full screen capture
- [x] Region-specific capture
- [x] Multiple image formats (PNG/JPG)
- [x] Error handling and edge cases

### Phase 3: Keyboard Automation ✅
- [x] SendKeys-based automation
- [x] Key combination support
- [x] Special key handling
- [x] Text input
- [x] Configurable delays

### Phase 4: Revit Integration (Next)
- [ ] Revit window detection
- [ ] Revit-specific shortcuts
- [ ] Property panel capture
- [ ] Model state analysis
- [ ] Warning detection

### Phase 5: Advanced Features (Future)
- [ ] Window management
- [ ] Multi-monitor support
- [ ] Batch operations
- [ ] Workflow recording/replay
- [ ] Integration with Revit API

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

## 🛠️ Troubleshooting

### PowerShell Execution Policy
If you get execution policy errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Screen Capture Issues
- Ensure no other applications are blocking screen capture
- Check if UAC prompts are preventing capture
- Verify PowerShell can access System.Drawing assemblies

### Keyboard Automation Issues
- Make sure the target window is active and ready for input
- Some applications may block SendKeys (security feature)
- Check for focus issues between windows

## 📄 License

MIT License - See LICENSE file for details.
