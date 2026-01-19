# DecisionTrace Frontend

Next.js frontend for the DecisionTrace AI decision journal.

## Features

- **Modern UI**: Built with Next.js 15 and React 19
- **Theme Toggle**: Light/dark mode with system preference detection
- **Smooth Animations**: Framer Motion with accessibility support
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Type Safety**: Full TypeScript coverage
- **Component Library**: shadcn/ui components

## Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

1. **Install dependencies:**
```bash
npm install
```

2. **Configure environment:**
Create `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Start development server:**
```bash
npm run dev
```

Visit http://localhost:3000

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── app/                  # Next.js App Router pages
│   ├── page.tsx         # Home page
│   ├── new/             # Create decision
│   ├── analysis/        # Decision list
│   ├── decision/[id]/   # Decision detail
│   └── reflection/[id]/ # Add reflection
├── components/          # React components
│   ├── ui/             # shadcn/ui components
│   ├── DecisionCard.tsx
│   ├── LoadingPipeline.tsx
│   ├── BiasReportView.tsx
│   ├── OutcomeScenariosView.tsx
│   ├── ReflectionView.tsx
│   ├── ThemeProvider.tsx
│   ├── ThemeToggle.tsx
│   └── PageTransition.tsx
├── hooks/              # Custom React hooks
│   └── useReducedMotion.ts
├── lib/                # Utilities
│   ├── api.ts         # API client
│   ├── types.ts       # TypeScript types
│   └── utils.ts       # Helper functions
└── public/            # Static assets
```

## Key Technologies

- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS v4**: Utility-first styling
- **Framer Motion**: Animation library
- **next-themes**: Theme management
- **shadcn/ui**: Component library
- **Radix UI**: Accessible primitives

## Features

### Theme System
- Light and dark modes
- System preference detection
- Persistent user preference
- Smooth transitions

### Animations
- Page transitions
- Component animations
- Loading states
- Respects `prefers-reduced-motion`

### Accessibility
- WCAG AA compliant
- Keyboard navigation
- Screen reader support
- Reduced motion support

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |

## Development

### Adding Components

Use shadcn/ui CLI:
```bash
npx shadcn@latest add [component-name]
```

### Type Checking

```bash
npm run build
```

## Deployment

### Vercel (Recommended)

1. Connect GitHub repository
2. Set environment variable: `NEXT_PUBLIC_API_URL`
3. Deploy automatically on push

### Other Platforms

Build the application:
```bash
npm run build
```

Start production server:
```bash
npm start
```

## License

MIT License
