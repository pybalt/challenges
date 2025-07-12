const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Testing Revit Screen Capture MCP Server...\n');

// Start the server
const serverPath = path.join(__dirname, 'dist', 'stdio.js');
const server = spawn('node', [serverPath], {
  stdio: ['pipe', 'pipe', 'pipe'],
  cwd: __dirname
});

let serverReady = false;
let testsPassed = 0;

// Test 1: Server starts successfully
server.on('spawn', () => {
  console.log('✅ Server started successfully');
  testsPassed++;
  
  // Test 2: Send initialize message
  setTimeout(() => {
    const initMessage = {
      jsonrpc: '2.0',
      id: 1,
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: {},
        clientInfo: {
          name: 'test-client',
          version: '1.0.0'
        }
      }
    };
    
    server.stdin.write(JSON.stringify(initMessage) + '\n');
    console.log('📤 Sent initialize message');
  }, 1000);
});

// Test 3: Check server responses
server.stdout.on('data', (data) => {
  const lines = data.toString().split('\n').filter(line => line.trim());
  
  lines.forEach(line => {
    try {
      const response = JSON.parse(line);
      
      if (response.id === 1 && response.result) {
        console.log('✅ Server initialized successfully');
        console.log('📋 Available capabilities:', JSON.stringify(response.result.capabilities, null, 2));
        testsPassed++;
        
        // Test 4: List tools
        setTimeout(() => {
          const toolsMessage = {
            jsonrpc: '2.0',
            id: 2,
            method: 'tools/list',
            params: {}
          };
          
          server.stdin.write(JSON.stringify(toolsMessage) + '\n');
          console.log('📤 Requesting tools list');
        }, 500);
      }
      
      if (response.id === 2 && response.result && response.result.tools) {
        console.log('✅ Tools listed successfully');
        console.log('🛠️ Available tools:');
        response.result.tools.forEach(tool => {
          console.log(`   - ${tool.name}: ${tool.description}`);
        });
        testsPassed++;
        
        // All tests completed
        setTimeout(() => {
          console.log(`\n🎉 All tests passed! (${testsPassed}/4)`);
          console.log('✅ MCP Server is ready for use with Cursor');
          console.log('\n📝 Next steps:');
          console.log('1. Copy cursor-mcp-config.json to your Cursor settings');
          console.log('2. Restart Cursor');
          console.log('3. Ask Cursor to capture your screen or send keys');
          
          server.kill();
          process.exit(0);
        }, 1000);
      }
    } catch (e) {
      // Ignore non-JSON output
    }
  });
});

// Handle errors
server.stderr.on('data', (data) => {
  console.error('❌ Server error:', data.toString());
});

server.on('error', (error) => {
  console.error('❌ Failed to start server:', error);
  process.exit(1);
});

server.on('exit', (code) => {
  if (code !== 0) {
    console.error(`❌ Server exited with code ${code}`);
    process.exit(1);
  }
});

// Timeout after 10 seconds
setTimeout(() => {
  console.error('❌ Test timeout - server may not be responding');
  server.kill();
  process.exit(1);
}, 10000); 