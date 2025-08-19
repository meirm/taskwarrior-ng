import React from 'react';
import { Card } from '@/components/ui/card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import { 
  CheckCircle2, 
  Code2, 
  Zap, 
  Shield, 
  Globe, 
  Server,
  Terminal,
  Layers,
  GitBranch,
  ExternalLink
} from 'lucide-react';

export function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">
          TaskWarrior <Badge className="ml-2 text-lg">MCP Edition</Badge>
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-6">
          A modern task management system powered by Model Context Protocol
        </p>
        <div className="flex justify-center gap-4">
          <Badge variant="outline" className="px-3 py-1">
            <Terminal className="w-4 h-4 mr-1" />
            Version 2.0.0
          </Badge>
          <Badge variant="outline" className="px-3 py-1">
            <Server className="w-4 h-4 mr-1" />
            MCPO Powered
          </Badge>
          <Badge variant="outline" className="px-3 py-1">
            <Shield className="w-4 h-4 mr-1" />
            API Secured
          </Badge>
        </div>
      </div>

      {/* TaskWarrior CLI Credits */}
      <Card className="p-6 mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-blue-200 dark:border-blue-800">
        <h2 className="text-2xl font-semibold mb-4 flex items-center">
          <Terminal className="w-6 h-6 mr-2 text-blue-600 dark:text-blue-400" />
          Powered by TaskWarrior
        </h2>
        <div className="space-y-4">
          <p className="text-gray-700 dark:text-gray-300">
            <strong>TaskWarrior</strong> is the powerful command-line task management tool that does the heavy lifting 
            behind this application. It's a feature-rich, open-source task manager that has been helping people 
            stay organized since 2006.
          </p>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold mb-2 text-blue-700 dark:text-blue-400">What is TaskWarrior?</h3>
              <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                <li>• Command-line task management tool</li>
                <li>• Manages tasks with priorities, projects, tags, and due dates</li>
                <li>• Powerful filtering and reporting capabilities</li>
                <li>• Syncs across devices with TaskServer</li>
                <li>• Extensible with hooks and scripts</li>
                <li>• Active development and community since 2006</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-2 text-blue-700 dark:text-blue-400">Our Integration</h3>
              <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                <li>• MCP Server wraps TaskWarrior CLI commands</li>
                <li>• Python tasklib provides programmatic access</li>
                <li>• MCPO exposes functionality as REST API</li>
                <li>• React frontend provides modern UI</li>
                <li>• Full TaskWarrior feature compatibility</li>
                <li>• Real-time sync with TaskWarrior database</li>
              </ul>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 mt-4">
            <p className="text-sm mb-3">
              <strong>Credits & Acknowledgments:</strong>
            </p>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="text-blue-600 dark:text-blue-400 mr-2">▸</span>
                <span>
                  <strong>TaskWarrior</strong> - Created by Paul Beckingham and the TaskWarrior team
                  <br />
                  <a href="https://taskwarrior.org" target="_blank" rel="noopener noreferrer" 
                     className="text-blue-600 dark:text-blue-400 hover:underline ml-2">
                    taskwarrior.org
                  </a>
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 dark:text-blue-400 mr-2">▸</span>
                <span>
                  <strong>tasklib</strong> - Python library for TaskWarrior integration
                  <br />
                  <a href="https://github.com/robgolding/tasklib" target="_blank" rel="noopener noreferrer"
                     className="text-blue-600 dark:text-blue-400 hover:underline ml-2">
                    github.com/robgolding/tasklib
                  </a>
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 dark:text-blue-400 mr-2">▸</span>
                <span>
                  <strong>MCP (Model Context Protocol)</strong> - By Anthropic
                  <br />
                  <a href="https://modelcontextprotocol.io" target="_blank" rel="noopener noreferrer"
                     className="text-blue-600 dark:text-blue-400 hover:underline ml-2">
                    modelcontextprotocol.io
                  </a>
                </span>
              </li>
            </ul>
          </div>

          <div className="flex gap-3 mt-4">
            <Button
              variant="outline"
              onClick={() => window.open('https://taskwarrior.org/docs/', '_blank')}
            >
              <Terminal className="w-4 h-4 mr-2" />
              TaskWarrior Docs
            </Button>
            <Button
              variant="outline"
              onClick={() => window.open('https://github.com/GothenburgBitFactory/taskwarrior', '_blank')}
            >
              <GitBranch className="w-4 h-4 mr-2" />
              TaskWarrior GitHub
            </Button>
          </div>
        </div>
      </Card>

      {/* MCPO Integration */}
      <Card className="p-6 mb-8 bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20">
        <h2 className="text-2xl font-semibold mb-4 flex items-center">
          <Server className="w-6 h-6 mr-2" />
          Powered by MCPO
        </h2>
        <div className="space-y-4">
          <p className="text-gray-700 dark:text-gray-300">
            <strong>MCPO (Model Context Protocol to OpenAPI)</strong> is the bridge that enables both this web interface 
            and AI agents to interact with the same TaskWarrior backend seamlessly.
          </p>
          
          <div className="bg-white/80 dark:bg-gray-800/80 rounded-lg p-4">
            <h3 className="font-semibold mb-2 text-lg">🤖 AI-Ready Architecture</h3>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="text-purple-600 dark:text-purple-400 mr-2">▸</span>
                <span>
                  <strong>Unified Backend:</strong> The same MCP server serves both the web UI and AI assistants
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-purple-600 dark:text-purple-400 mr-2">▸</span>
                <span>
                  <strong>Claude Desktop Integration:</strong> AI agents can manage your tasks through natural language
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-purple-600 dark:text-purple-400 mr-2">▸</span>
                <span>
                  <strong>OpenAPI Standards:</strong> RESTful API with automatic documentation and type safety
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-purple-600 dark:text-purple-400 mr-2">▸</span>
                <span>
                  <strong>Real-time Sync:</strong> Changes made by AI are instantly visible in the web interface
                </span>
              </li>
            </ul>
          </div>

          <div className="bg-white/80 dark:bg-gray-800/80 rounded-lg p-4">
            <p className="text-sm mb-2">
              <strong>How it works:</strong>
            </p>
            <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <p>1. MCP Server exposes TaskWarrior operations as protocol tools</p>
              <p>2. MCPO translates these tools into REST API endpoints</p>
              <p>3. Both web frontend and AI agents use the same API</p>
              <p>4. All changes are synchronized through TaskWarrior CLI</p>
            </div>
          </div>

          <div className="flex gap-3">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => window.open('https://github.com/modelcontextprotocol/mcpo', '_blank')}
            >
              <ExternalLink className="w-4 h-4 mr-2" />
              MCPO on GitHub
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => window.open('https://modelcontextprotocol.io', '_blank')}
            >
              <ExternalLink className="w-4 h-4 mr-2" />
              Learn about MCP
            </Button>
          </div>
        </div>
      </Card>

      {/* Architecture Overview */}
      <Card className="p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4 flex items-center">
          <Layers className="w-6 h-6 mr-2" />
          Architecture Overview
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="text-center p-4 border rounded-lg">
            <div className="text-3xl mb-2">🎨</div>
            <h3 className="font-semibold mb-1">React Frontend</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              TypeScript + Tailwind CSS
            </p>
          </div>
          <div className="text-center p-4 border rounded-lg bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700">
            <div className="text-3xl mb-2">🔗</div>
            <h3 className="font-semibold mb-1">MCPO Server</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              REST API + OpenAPI Docs
            </p>
          </div>
          <div className="text-center p-4 border rounded-lg">
            <div className="text-3xl mb-2">⚙️</div>
            <h3 className="font-semibold mb-1">MCP Server</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              TaskWarrior Integration
            </p>
          </div>
        </div>
      </Card>

      {/* Key Features */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Zap className="w-5 h-5 mr-2 text-yellow-500" />
            MCP Integration
          </h2>
          <ul className="space-y-2">
            <li className="flex items-start">
              <CheckCircle2 className="w-5 h-5 mr-2 text-green-500 mt-0.5" />
              <span>Direct Model Context Protocol support</span>
            </li>
            <li className="flex items-start">
              <CheckCircle2 className="w-5 h-5 mr-2 text-green-500 mt-0.5" />
              <span>19+ MCP tools for comprehensive task management</span>
            </li>
            <li className="flex items-start">
              <CheckCircle2 className="w-5 h-5 mr-2 text-green-500 mt-0.5" />
              <span>Smart prompts for AI-assisted planning</span>
            </li>
            <li className="flex items-start">
              <CheckCircle2 className="w-5 h-5 mr-2 text-green-500 mt-0.5" />
              <span>Real-time task synchronization</span>
            </li>
          </ul>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Globe className="w-5 h-5 mr-2 text-blue-500" />
            MCPO Features
          </h2>
          <ul className="space-y-2">
            <li className="flex items-start">
              <CheckCircle2 className="w-5 h-5 mr-2 text-green-500 mt-0.5" />
              <span>OpenAPI documentation at /docs</span>
            </li>
            <li className="flex items-start">
              <CheckCircle2 className="w-5 h-5 mr-2 text-green-500 mt-0.5" />
              <span>Bearer token authentication</span>
            </li>
            <li className="flex items-start">
              <CheckCircle2 className="w-5 h-5 mr-2 text-green-500 mt-0.5" />
              <span>CORS support for web applications</span>
            </li>
            <li className="flex items-start">
              <CheckCircle2 className="w-5 h-5 mr-2 text-green-500 mt-0.5" />
              <span>Automatic REST endpoint generation</span>
            </li>
          </ul>
        </Card>
      </div>

      {/* Technical Stack */}
      <Card className="p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4 flex items-center">
          <Code2 className="w-6 h-6 mr-2" />
          Technical Stack
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <h3 className="font-semibold mb-2 text-blue-600 dark:text-blue-400">Frontend</h3>
            <ul className="space-y-1 text-sm">
              <li>• React 18 with TypeScript</li>
              <li>• Vite for fast development</li>
              <li>• Tailwind CSS for styling</li>
              <li>• Zustand for state management</li>
              <li>• Custom MCPO client library</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2 text-green-600 dark:text-green-400">MCPO Layer</h3>
            <ul className="space-y-1 text-sm">
              <li>• MCPO server wrapper</li>
              <li>• FastAPI/Uvicorn backend</li>
              <li>• OpenAPI specification</li>
              <li>• Bearer authentication</li>
              <li>• Automatic tool exposure</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2 text-purple-600 dark:text-purple-400">Backend</h3>
            <ul className="space-y-1 text-sm">
              <li>• Python MCP server</li>
              <li>• TaskWarrior integration</li>
              <li>• tasklib Python library</li>
              <li>• Modular architecture</li>
              <li>• Pydantic validation</li>
            </ul>
          </div>
        </div>
      </Card>

      {/* API Information */}
      <Card className="p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4 flex items-center">
          <Terminal className="w-6 h-6 mr-2" />
          API Access
        </h2>
        <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4 mb-4">
          <p className="text-sm font-mono mb-2">
            <span className="text-gray-500">Base URL:</span> {window.location.protocol}//{window.location.hostname}:8885
          </p>
          <p className="text-sm font-mono mb-2">
            <span className="text-gray-500">API Docs:</span> {window.location.protocol}//{window.location.hostname}:8885/docs
          </p>
          <p className="text-sm font-mono">
            <span className="text-gray-500">Auth Header:</span> Authorization: Bearer taskwarrior-secret-key
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={() => window.open(`${window.location.protocol}//${window.location.hostname}:8885/docs`, '_blank')}
          >
            <ExternalLink className="w-4 h-4 mr-2" />
            View API Documentation
          </Button>
        </div>
      </Card>

      {/* MCP Tools */}
      <Card className="p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4 flex items-center">
          <GitBranch className="w-6 h-6 mr-2" />
          Available MCP Tools
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {[
            'add_task', 'list_tasks', 'get_task', 'modify_task',
            'complete_task', 'uncomplete_task', 'delete_task', 'start_task',
            'stop_task', 'get_projects', 'get_tags', 'get_summary',
            'batch_complete_tasks', 'batch_delete_tasks', 'batch_modify_tasks',
            'purge_tasks', 'restore_task', 'batch_start_tasks', 'batch_stop_tasks'
          ].map(tool => (
            <Badge key={tool} variant="outline" className="justify-center py-1">
              {tool}
            </Badge>
          ))}
        </div>
      </Card>

      {/* Contributing */}
      <Card className="p-6">
        <h2 className="text-2xl font-semibold mb-4">Contributing</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          TaskWarrior MCP Edition is an open-source project that bridges the powerful TaskWarrior 
          task management system with modern AI capabilities through the Model Context Protocol.
        </p>
        <div className="flex gap-3">
          <Button variant="outline">
            <GitBranch className="w-4 h-4 mr-2" />
            View on GitHub
          </Button>
          <Button variant="outline">
            <Terminal className="w-4 h-4 mr-2" />
            TaskWarrior Docs
          </Button>
        </div>
      </Card>
    </div>
  );
}