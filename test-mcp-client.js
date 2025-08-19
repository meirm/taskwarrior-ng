#!/usr/bin/env node

/**
 * Test MCP Client for TaskWarrior MCP Server
 * This script tests the stdio communication with the MCP server
 */

import { spawn } from 'child_process';
import readline from 'readline';

class TestMCPClient {
  constructor() {
    this.process = null;
    this.requestId = 0;
    this.pendingRequests = new Map();
    this.buffer = '';
  }

  async start() {
    console.log('🚀 Starting MCP test client...\n');
    
    return new Promise((resolve, reject) => {
      // Spawn the MCP server process
      const pythonPath = 'python3';
      const serverPath = 'apps/mcp-server/src/taskwarrior_mcp_server.py';
      
      console.log(`📦 Spawning process: ${pythonPath} ${serverPath}`);
      
      this.process = spawn(pythonPath, [serverPath], {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env }
      });

      // Handle stdout (JSON-RPC responses)
      this.process.stdout.on('data', (data) => {
        this.buffer += data.toString();
        this.processBuffer();
      });

      // Handle stderr (logging)
      this.process.stderr.on('data', (data) => {
        console.log('📝 Server log:', data.toString().trim());
      });

      // Handle errors
      this.process.on('error', (error) => {
        console.error('❌ Process error:', error);
        reject(error);
      });

      // Handle exit
      this.process.on('exit', (code) => {
        console.log(`\n💤 Server process exited with code ${code}`);
      });

      // Give the server a moment to start
      setTimeout(() => {
        console.log('✅ MCP server process started\n');
        resolve();
      }, 1000);
    });
  }

  processBuffer() {
    const lines = this.buffer.split('\n');
    this.buffer = lines.pop() || ''; // Keep incomplete line in buffer

    for (const line of lines) {
      if (line.trim()) {
        try {
          const response = JSON.parse(line);
          console.log('📥 Received:', JSON.stringify(response, null, 2));
          
          if (response.id !== undefined && this.pendingRequests.has(response.id)) {
            const { resolve } = this.pendingRequests.get(response.id);
            this.pendingRequests.delete(response.id);
            resolve(response);
          }
        } catch (error) {
          // Not JSON, might be a notification or other output
          console.log('📄 Non-JSON output:', line);
        }
      }
    }
  }

  async sendRequest(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++this.requestId;
      const request = {
        jsonrpc: '2.0',
        id,
        method,
        params
      };

      console.log('📤 Sending:', JSON.stringify(request, null, 2));
      
      this.pendingRequests.set(id, { resolve, reject });

      // Set timeout
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error(`Request ${id} timed out (method: ${method})`));
        }
      }, 10000); // 10 second timeout

      try {
        this.process.stdin.write(JSON.stringify(request) + '\n');
      } catch (error) {
        this.pendingRequests.delete(id);
        reject(error);
      }
    });
  }

  async testInitialize() {
    console.log('🔧 Testing initialize...\n');
    try {
      const response = await this.sendRequest('initialize', {
        protocolVersion: '2024-11-05',
        capabilities: {
          roots: {
            listChanged: true
          },
          sampling: {}
        },
        clientInfo: {
          name: 'test-mcp-client',
          version: '1.0.0'
        }
      });
      console.log('✅ Initialize successful\n');
      
      // Send the 'initialized' notification
      console.log('📤 Sending initialized notification...\n');
      const notification = {
        jsonrpc: '2.0',
        method: 'notifications/initialized',
        params: {}
      };
      this.process.stdin.write(JSON.stringify(notification) + '\n');
      
      // Wait a moment for the server to process the notification
      await new Promise(resolve => setTimeout(resolve, 500));
      
      return response;
    } catch (error) {
      console.error('❌ Initialize failed:', error.message);
      throw error;
    }
  }

  async testListTools() {
    console.log('🔧 Testing tools/list...\n');
    try {
      const response = await this.sendRequest('tools/list', {});
      console.log(`✅ Found ${response.result?.tools?.length || 0} tools\n`);
      
      // List first 5 tools
      if (response.result?.tools) {
        console.log('Available tools:');
        response.result.tools.slice(0, 5).forEach(tool => {
          console.log(`  - ${tool.name}: ${tool.description}`);
        });
        if (response.result.tools.length > 5) {
          console.log(`  ... and ${response.result.tools.length - 5} more`);
        }
      }
      return response;
    } catch (error) {
      console.error('❌ List tools failed:', error.message);
      throw error;
    }
  }

  async testCallTool(toolName, args = {}) {
    console.log(`\n🔧 Testing tool: ${toolName}...\n`);
    try {
      const response = await this.sendRequest('tools/call', {
        name: toolName,
        arguments: args
      });
      console.log(`✅ Tool ${toolName} executed successfully\n`);
      return response;
    } catch (error) {
      console.error(`❌ Tool ${toolName} failed:`, error.message);
      throw error;
    }
  }

  async testListResources() {
    console.log('\n📚 Testing resources/list...\n');
    try {
      const response = await this.sendRequest('resources/list', {});
      console.log(`✅ Found ${response.result?.resources?.length || 0} resources\n`);
      
      if (response.result?.resources) {
        console.log('Available resources:');
        response.result.resources.forEach(resource => {
          console.log(`  - ${resource.uri}: ${resource.name}`);
        });
      }
      return response;
    } catch (error) {
      console.error('❌ List resources failed:', error.message);
      throw error;
    }
  }

  async testListPrompts() {
    console.log('\n💭 Testing prompts/list...\n');
    try {
      const response = await this.sendRequest('prompts/list', {});
      console.log(`✅ Found ${response.result?.prompts?.length || 0} prompts\n`);
      
      if (response.result?.prompts) {
        console.log('Available prompts:');
        response.result.prompts.forEach(prompt => {
          console.log(`  - ${prompt.name}: ${prompt.description}`);
        });
      }
      return response;
    } catch (error) {
      console.error('❌ List prompts failed:', error.message);
      throw error;
    }
  }

  async stop() {
    if (this.process) {
      console.log('\n👋 Stopping MCP server...');
      this.process.kill();
      this.process = null;
    }
  }
}

async function runTests() {
  const client = new TestMCPClient();
  
  try {
    // Start the server
    await client.start();
    
    // Wait a bit for server to fully initialize
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Run tests
    console.log('=' .repeat(60));
    console.log('Starting MCP Protocol Tests');
    console.log('=' .repeat(60) + '\n');
    
    // Test initialize
    await client.testInitialize();
    
    // Test listing tools
    await client.testListTools();
    
    // Test listing resources
    await client.testListResources();
    
    // Test listing prompts
    await client.testListPrompts();
    
    // Test calling a simple tool
    await client.testCallTool('list_tasks', {
      status: 'pending',
      limit: 5
    });
    
    // Test getting summary
    await client.testCallTool('get_summary', {});
    
    console.log('\n' + '=' .repeat(60));
    console.log('✅ All tests completed successfully!');
    console.log('=' .repeat(60));
    
  } catch (error) {
    console.error('\n❌ Test failed:', error);
  } finally {
    // Clean up
    await client.stop();
  }
}

// Handle Ctrl+C
process.on('SIGINT', () => {
  console.log('\n\n🛑 Interrupted by user');
  process.exit(0);
});

// Run the tests
console.log('TaskWarrior MCP Server Test Client');
console.log('===================================\n');
runTests().catch(console.error);