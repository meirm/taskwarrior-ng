# TaskWarrior Frontend

Modern React/TypeScript frontend for TaskWarrior task management.

## Features

- ✨ **Modern UI/UX** - Clean, responsive design with Tailwind CSS
- 🚀 **Fast Performance** - Built with Vite and optimized for speed
- 📱 **Mobile Responsive** - Works seamlessly across all devices
- 🎯 **Task Management** - Complete CRUD operations for tasks
- 📊 **Dashboard** - Visual overview of your task progress
- 🏷️ **Projects & Tags** - Organize tasks with projects and tags
- ⚡ **Batch Operations** - Efficiently manage multiple tasks at once
- 🔍 **Advanced Filtering** - Search and filter tasks by multiple criteria
- ⏰ **Time Tracking** - Start/stop timers for task time tracking
- 📈 **Priority Management** - Visual urgency indicators and priority levels

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Forms**: React Hook Form with Zod validation
- **Icons**: Lucide React
- **Routing**: React Router
- **HTTP Client**: Fetch API with custom wrapper

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## API Integration

The frontend communicates with the TaskWarrior MCP server through an API bridge server running on port 3001. The API client automatically handles:

- Request/response serialization
- Error handling
- Type safety
- Authentication (when implemented)

## Component Architecture

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Base UI components (Button, Input, etc.)
│   ├── TaskCard.tsx    # Individual task display
│   ├── TaskForm.tsx    # Task creation/editing
│   ├── TaskList.tsx    # Task list with filtering
│   └── Layout.tsx      # Application layout
├── pages/              # Page components
│   ├── DashboardPage.tsx
│   └── TasksPage.tsx
├── stores/             # Zustand state management
├── services/           # API client and external services
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── hooks/              # Custom React hooks
```

## State Management

Uses Zustand for efficient state management with features:

- Task data synchronization
- UI state management
- Batch operation handling
- Error state tracking
- Filter and search state

## Performance Optimizations

- **Code Splitting**: Automatic route-based splitting
- **Tree Shaking**: Unused code elimination
- **Asset Optimization**: Image and bundle optimization
- **Memoization**: React.memo and useMemo for expensive operations
- **Lazy Loading**: Components loaded on demand

## Responsive Design

Mobile-first responsive design with breakpoints:
- Mobile: 320px+
- Tablet: 768px+
- Desktop: 1024px+
- Large Desktop: 1280px+

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler

### Environment Variables

Create a `.env` file for local development:

```bash
VITE_API_URL=http://localhost:3001/api
```

### Code Style

- TypeScript strict mode enabled
- ESLint with React and TypeScript rules
- Prettier for code formatting
- Conventional commit messages

## Contributing

1. Follow the existing code style
2. Write meaningful commit messages
3. Add types for all new interfaces
4. Test components in multiple screen sizes
5. Update documentation as needed

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- iOS Safari 14+
- Android Chrome 88+