# LegalAI Frontend

A modern, responsive React application built with Next.js that provides an intuitive interface for the LegalAI legal information retrieval system. Features an interactive chat interface, document discovery, and personalized recommendations.

## Features

- **Interactive Chat Interface**: Modern chat UI for legal queries with real-time responses
- **Responsive Design**: Mobile-first design that works across all devices
- **Document Discovery**: Explore and search through legal documents
- **Query History**: Track and revisit previous legal conversations
- **Personalized Recommendations**: Get tailored legal content suggestions
- **Modern UI Components**: Built with Radix UI and styled with Tailwind CSS
- **Fast Performance**: Powered by Next.js 15 with Turbopack for lightning-fast builds

## Architecture

The frontend follows Next.js App Router structure with:

```
frontend/
├── src/
│   ├── app/                    # App Router pages and layouts
│   │   ├── layout.js          # Root layout
│   │   ├── page.js            # Home page
│   │   ├── globals.css        # Global styles
│   │   ├── _components/       # Page-specific components
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── ChatBox.jsx
│   │   │   ├── AppsideBar.jsx
│   │   │   ├── DiscoverInterface.jsx
│   │   │   ├── HistoryInterface.jsx
│   │   │   └── RecommendationInterface.jsx
│   │   ├── discover/          # Discovery page
│   │   ├── history/           # History page
│   │   ├── recommendations/   # Recommendations page
│   │   └── api/              # API routes
│   ├── components/           # Reusable UI components
│   │   └── ui/              # Shadcn/ui components
│   ├── hooks/               # Custom React hooks
│   └── lib/                 # Utility functions
├── public/                  # Static assets
├── package.json            # Dependencies and scripts
└── next.config.mjs         # Next.js configuration
```

## Quick Start

### Prerequisites

- Node.js 18 or higher
- npm, yarn, or pnpm package manager

### Installation

1. **Navigate to frontend directory**

   ```bash
   cd frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Run the development server**

   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

4. **Open the application**

   Navigate to [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## User Interface

### Home Page (`/`)

- **Chat Interface**: Primary interaction point for legal queries
- **Quick Start**: Get started with sample questions
- **Modern Design**: Clean, professional interface optimized for legal professionals

### Discovery Page (`/discover`)

- **Document Explorer**: Browse available legal documents
- **Search Functionality**: Find specific legal topics
- **Category Filtering**: Organize content by legal areas

### History Page (`/history`)

- **Query Timeline**: View past legal questions and responses
- **Search History**: Find previous conversations
- **Export Options**: Save important conversations

### Recommendations Page (`/recommendations`)

- **Personalized Content**: Legal topics tailored to your interests
- **Trending Topics**: Popular legal queries and topics
- **Smart Suggestions**: AI-powered content recommendations

## Technology Stack

### Core Framework

- **Next.js 15**: React framework with App Router
- **React 19**: Latest React with concurrent features
- **Turbopack**: Ultra-fast bundler for development

### Styling & UI

- **Tailwind CSS**: Utility-first CSS framework
- **Radix UI**: Accessible, unstyled UI components
- **Lucide React**: Beautiful, customizable icons
- **Class Variance Authority**: Component variant management

### State Management & Routing

- **React Hooks**: Built-in state management
- **React Router DOM**: Client-side routing
- **URL State**: Navigation state management

### Development Tools

- **ESLint**: Code linting and formatting
- **PostCSS**: CSS processing and optimization
- **Tailwind Scrollbar Hide**: Enhanced scrollbar styling

## Configuration

### Environment Variables

Create a `.env.local` file in the frontend directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional configurations
NEXT_PUBLIC_APP_NAME=LegalAI
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Tailwind Configuration

The project uses a custom Tailwind configuration in `tailwind.config.js`:

```javascript
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // Custom theme extensions
    },
  },
  plugins: [require("tailwind-scrollbar-hide")],
};
```

## Components

### Core Components

#### `ChatInterface`

The main chat component for legal queries:

```jsx
<ChatInterface
  initialQuery="Your legal question"
  initialResponse="AI response"
  isLoading={false}
/>
```

#### `ChatBox`

Quick start component for initiating conversations:

```jsx
<ChatBox
  onStartChat={(query) => handleQuery(query)}
  placeholder="Ask a legal question..."
/>
```

#### `AppsideBar`

Navigation sidebar with menu items:

```jsx
<AppsideBar currentPath="/discover" onNavigate={(path) => router.push(path)} />
```

### UI Components

Built with Radix UI primitives and styled with Tailwind:

- **Button**: Various button styles and states
- **Input**: Form input with validation states
- **Card**: Content containers with consistent styling
- **Badge**: Status and category indicators
- **Tooltip**: Contextual help and information
- **Scroll Area**: Enhanced scrollable regions
- **Dropdown Menu**: Context menus and navigation
- **Separator**: Visual content dividers
- **Sheet**: Slide-out panels and modals
- **Skeleton**: Loading state placeholders

## Development

### Available Scripts

```bash
# Development with Turbopack
npm run dev

# Production build with Turbopack
npm run build

# Start production server
npm run start

# Lint code
npm run lint
```

### Project Structure Best Practices

1. **Components**: Reusable components in `/components/ui/`
2. **Pages**: App Router pages in `/app/`
3. **Styles**: Global styles in `/app/globals.css`
4. **Utilities**: Helper functions in `/lib/`
5. **Hooks**: Custom hooks in `/hooks/`

### Adding New Components

1. Create component in appropriate directory
2. Follow naming conventions (PascalCase for components)
3. Export from index files for clean imports
4. Include prop types and documentation

Example component structure:

```jsx
"use client";

import React from "react";
import { cn } from "@/lib/utils";

export function MyComponent({ className, children, ...props }) {
  return (
    <div className={cn("base-styles", className)} {...props}>
      {children}
    </div>
  );
}
```

## API Integration

The frontend communicates with the backend through REST API calls:

```javascript
// Chat API
const response = await fetch("/api/chat/get_ai_response", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ query, history }),
});

// Search API
const documents = await fetch("/api/get_docs/search", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ query }),
});

// Recommendations API
const recommendations = await fetch("/api/recommendations", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ username }),
});
```

## Responsive Design

The application is built mobile-first with responsive breakpoints:

- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

Key responsive features:

- Adaptive layouts using CSS Grid and Flexbox
- Touch-friendly interface elements
- Optimized font sizes and spacing
- Collapsible navigation on mobile

## Troubleshooting

### Common Issues

1. **Build Errors**: Clear `.next` folder and reinstall dependencies
2. **Styling Issues**: Check Tailwind configuration and class names
3. **API Errors**: Verify backend is running and CORS is configured
4. **Routing Issues**: Ensure proper App Router structure

### Performance Optimization

- **Image Optimization**: Use Next.js `Image` component
- **Code Splitting**: Leverage dynamic imports for large components
- **Bundle Analysis**: Use `@next/bundle-analyzer` to analyze bundle size
- **Caching**: Implement proper caching strategies

## Testing

### Setup Testing Environment

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom jest jest-environment-jsdom
```

### Example Test

```javascript
import { render, screen } from "@testing-library/react";
import { ChatInterface } from "../components/ChatInterface";

test("renders chat interface", () => {
  render(<ChatInterface />);
  const chatInput = screen.getByPlaceholderText(/ask a legal question/i);
  expect(chatInput).toBeInTheDocument();
});
```

## Contributing

1. Follow React and Next.js best practices
2. Use TypeScript for new components (when applicable)
3. Write meaningful component and prop names
4. Add proper accessibility attributes
5. Test components on multiple screen sizes
6. Update documentation for new features

## License

This frontend application is part of the LegalAI project and follows the same MIT License.
