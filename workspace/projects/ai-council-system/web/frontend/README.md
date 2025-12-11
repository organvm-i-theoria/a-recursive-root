# AI Council System - Web Frontend

React/Next.js frontend for viewing and interacting with AI Council debates.

## Features

- **Live Debate Viewer**: Real-time debate streaming with WebSocket updates
- **Agent Dashboard**: View all AI agents and their personalities
- **Topic Browser**: Browse and search available debate topics
- **Debate History**: View past debates and transcripts
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Modern dark UI optimized for long viewing sessions

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Real-time**: Socket.IO Client
- **HTTP Client**: Axios
- **Markdown**: React Markdown

## Setup

### Development

```bash
cd web/frontend

# Install dependencies
npm install

# Set environment variables
export NEXT_PUBLIC_API_URL="http://localhost:8000"
export NEXT_PUBLIC_WS_URL="ws://localhost:8000/ws"

# Run development server
npm run dev
```

Visit http://localhost:3000

### Production Build

```bash
npm run build
npm run start
```

## Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

For production:
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com/ws
```

## Pages

### Home (`/`)
- Dashboard with active debates
- System status
- Quick navigation

### Debate Viewer (`/debate/[id]`)
- Live debate transcript
- Council member info
- Voting results
- Real-time updates via WebSocket
- Auto-scrolling to latest messages

### Agent Dashboard (`/agents`)
- List all AI agents
- View personality profiles
- Agent statistics
- Create new agents

### Topic Browser (`/topics`)
- Browse available topics
- Search and filter
- Start new debates
- View topic controversy scores

## Components

### Core Components

- `DebateViewer`: Main debate viewing interface
- `AgentCard`: Display agent personality and status
- `TopicCard`: Show topic details
- `VotingResults`: Visualize voting outcomes
- `ConnectionStatus`: Show WebSocket connection state

### Layout Components

- `Header`: Navigation and branding
- `Sidebar`: Contextual information
- `Footer`: System info and links

## WebSocket Events

The frontend listens for these events:

```typescript
// Connection
socket.on('connect', () => { /* Handle connection */ })
socket.on('disconnect', () => { /* Handle disconnection */ })

// Debate events
socket.on('debate_update', (data) => { /* Update debate state */ })
socket.on('agent_response', (data) => { /* Show new message */ })
socket.on('vote_cast', (data) => { /* Update votes */ })
socket.on('debate_completed', (data) => { /* Show results */ })
```

## API Integration

### REST Endpoints

```typescript
// Get debates
GET /api/v1/debates
GET /api/v1/debates/:id
GET /api/v1/debates/:id/transcript

// Get agents
GET /api/v1/agents
GET /api/v1/agents/:id
POST /api/v1/agents

// Get topics
GET /api/v1/topics

// Start debate
POST /api/v1/debates
```

## Styling

### Tailwind Configuration

Custom colors and animations defined in `tailwind.config.js`:

```javascript
colors: {
  primary: { /* Blue shades */ },
}
animation: {
  'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
}
```

### Custom CSS

Global styles in `app/globals.css`:
- Custom scrollbar
- Markdown formatting
- Gradient backgrounds
- Animations

## Development Tips

### Hot Reload

Next.js automatically reloads on file changes. Backend API changes require restart.

### TypeScript

All components use TypeScript. Run type checking:

```bash
npx tsc --noEmit
```

### Linting

```bash
npm run lint
```

### Debugging WebSocket

Open browser console to see WebSocket connection logs:

```javascript
// In browser console
localStorage.debug = '*'
```

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

### Static Export

For CDN deployment:

```bash
npm run build
# Deploy /out directory to CDN
```

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile: iOS Safari, Chrome Android

## Performance

### Optimizations

- Automatic code splitting
- Image optimization
- Font optimization
- CSS purging (unused styles removed)
- Gzip compression

### Monitoring

Use Vercel Analytics or self-hosted:

```typescript
// pages/_app.tsx
import { Analytics } from '@vercel/analytics/react'

export default function App({ Component, pageProps }) {
  return (
    <>
      <Component {...pageProps} />
      <Analytics />
    </>
  )
}
```

## Troubleshooting

### WebSocket Connection Failed

Check backend is running and CORS is configured:

```python
# In server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Errors

Verify API URL is correct:

```bash
echo $NEXT_PUBLIC_API_URL
curl $NEXT_PUBLIC_API_URL/health
```

### Build Errors

Clear cache and reinstall:

```bash
rm -rf .next node_modules
npm install
npm run build
```

## Contributing

When adding new features:

1. Create component in `src/components/`
2. Add TypeScript interfaces
3. Use Tailwind for styling
4. Add error handling
5. Update this README

## License

Part of AI Council System - see main project LICENSE
