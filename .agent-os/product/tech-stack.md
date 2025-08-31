# Technical Stack

## Application Framework
- **Frontend Framework**: React 18.3.1 with TypeScript 5.2.2
- **Build Tool**: Vite 5.3.4 with ES modules
- **Backend Framework**: Python FastMCP 2.11.3 with MCP Protocol 1.13.0
- **API Layer**: MCPO (Model Context Protocol to OpenAPI) wrapper

## Database System
- **Primary Database**: TaskWarrior SQLite database (native integration)
- **Task Library**: tasklib 2.5.1+ (Python TaskWarrior interface)
- **Data Validation**: Pydantic 2.0.0+ for type safety

## JavaScript Framework
- **Core Framework**: React 18.3.1
- **Router**: React Router DOM 6.26.0
- **State Management**: Zustand 4.5.4
- **Data Fetching**: TanStack React Query 5.51.0
- **Form Handling**: React Hook Form 7.52.0 with Zod 3.23.8 validation

## Import Strategy
- **Module System**: ES modules with Vite
- **Package Manager**: npm
- **Type System**: TypeScript with strict mode

## CSS Framework
- **Primary**: Tailwind CSS 3.4.7
- **PostCSS**: 8.4.40 with Autoprefixer 10.4.19
- **Responsive Design**: Mobile-first approach

## UI Component Library
- **Custom Components**: Built with Tailwind CSS
- **Icons**: Lucide React 0.427.0
- **Utilities**: clsx 2.1.1 for conditional classes
- **Date Handling**: date-fns 3.6.0

## Fonts Provider
- **System Fonts**: Inter (primary), system font stack fallback
- **Loading Strategy**: CSS font-display: swap

## Icon Library
- **Primary**: Lucide React (feather-style icons)
- **Format**: React components with TypeScript support

## Application Hosting
- **Development**: Vite dev server (localhost:3033)
- **Production**: Static site hosting compatible
- **Build Output**: Optimized SPA with code splitting

## Database Hosting
- **Local Development**: TaskWarrior local database (~/.task/)
- **Production**: TaskWarrior server instances
- **Data Location**: Configurable via MCP server settings

## Asset Hosting
- **Development**: Vite dev server
- **Production**: CDN compatible static assets
- **Optimization**: Vite build optimization with tree shaking

## Deployment Solution
- **Development**: Start-dev.sh script for orchestrated startup
- **Container Support**: Ready for Docker/Podman containerization
- **Process Management**: Multi-process coordination (Frontend + MCPO + MCP)

## Code Repository URL
- **Git Repository**: https://github.com/your-repo/taskwarrior-ng
- **Branch Strategy**: main branch with development workflow
- **Version Control**: Git with conventional commits