# Frontend - Kanban Board Application

## Overview

The frontend is a fully functional Next.js 16 Kanban board application with drag-and-drop support, card management, and column renaming. This is a pure frontend demo with in-memory state management (no backend integration yet).

## Technology Stack

- **Framework**: Next.js 16.1.6
- **React**: 19.2.3 (App Router)
- **Drag & Drop**: @dnd-kit (core, sortable, utilities)
- **Styling**: TailwindCSS 4 with PostCSS
- **Testing**: 
  - Unit tests: Vitest 3.2.4 with React Testing Library
  - E2E tests: Playwright 1.58.0
- **Package Manager**: npm (will migrate to uv in Docker)

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── globals.css       # TailwindCSS styles with CSS variables for theming
│   │   ├── layout.tsx        # Root layout
│   │   └── page.tsx          # Home page - renders KanbanBoard
│   ├── components/
│   │   ├── KanbanBoard.tsx       # Main board container with drag-drop context
│   │   ├── KanbanColumn.tsx      # Individual column with cards
│   │   ├── KanbanCard.tsx        # Draggable card component
│   │   ├── KanbanCardPreview.tsx # Preview card during drag
│   │   ├── NewCardForm.tsx       # Form to add new cards to a column
│   │   ├── KanbanBoard.test.tsx  # Unit tests for board component
│   └── lib/
│       ├── kanban.ts         # Data model and card movement logic
│       └── kanban.test.ts    # Unit tests for kanban utilities
├── tests/
│   ├── kanban.spec.ts        # E2E tests (Playwright)
│   ├── setup.ts              # Vitest setup
│   └── vitest.d.ts           # Vitest type definitions
└── public/                   # Static assets
```

## Core Data Model

### Types (src/lib/kanban.ts)

```typescript
type Card = {
  id: string;           // Format: "card-{number}"
  title: string;        // Card title (required)
  details: string;      // Card description/notes
};

type Column = {
  id: string;           // Format: "col-{columnType}"
  title: string;        // Column name (editable)
  cardIds: string[];    // Array of card IDs in this column
};

type BoardData = {
  columns: Column[];
  cards: Record<string, Card>;  // Cards indexed by ID for O(1) lookup
};
```

### Initial Data

5 fixed columns: Backlog, Discovery, In Progress, Review, Done
8 sample cards distributed across columns

## Component Architecture

### KanbanBoard (Main Container)

**State Management:**
- `board`: Current board data with columns and cards
- `activeCardId`: ID of card being dragged (for preview overlay)

**Responsibilities:**
- Manages DndContext for drag-drop functionality
- Handles drag events (handleDragStart, handleDragEnd)
- Manages column rename, card add, card delete operations
- Renders header with board info and column pills
- Renders grid of KanbanColumn components

**Key Features:**
- Uses `useSensors` with PointerSensor (6px activation distance)
- `closestCorners` collision detection algorithm
- Memoizes `cardsById` for performance

### KanbanColumn (Column Container)

**Props:**
- `column`: Column object
- `cards`: Array of Card objects
- `onRename`: Callback to rename column
- `onAddCard`: Callback to add new card
- `onDeleteCard`: Callback to delete card

**Responsibilities:**
- Renders column header with title input
- Sets up SortableContext for its cards
- Renders list of KanbanCard components
- Shows empty state ("Drop a card here") when no cards
- Renders NewCardForm at bottom

### KanbanCard (Draggable Card)

**Props:**
- `card`: Card object
- `onDelete`: Callback to delete card

**Features:**
- Uses `useSortable` hook for drag-drop
- Applies transform/transition via CSS.Transform
- Shows opacity change during drag
- Delete button on card

### KanbanCardPreview (Drag Overlay Preview)

**Used by:** KanbanBoard during drag
**Purpose:** Shows what's being dragged in DragOverlay

### NewCardForm (Card Creation Form)

**Props:**
- `onAdd`: Callback with (title, details)

**Features:**
- Toggle between collapsed button and open form
- Title input (required)
- Details textarea (optional)
- Submit/Cancel buttons
- Resets form after add

## Key Functions (kanban.ts)

### `moveCard(columns, activeId, overId)`
- Reorders cards within same column
- Moves cards between columns
- Drops cards at end of target column (if dropping on column itself)
- Returns new columns array

### `createId(prefix)`
- Generates IDs with prefix (e.g., "card-1", "col-a")

## Styling

### CSS Variables (globals.css)

```
--accent-yellow: #ecad0a
--primary-blue: #209dd7
--secondary-purple: #753991
--navy-dark: #032147
--gray-text: #888888
--stroke: border color
--surface: light background
--surface-strong: medium background
--shadow: drop shadow
```

Uses TailwindCSS utility classes with custom color variables.

## Testing Strategy

### Unit Tests (Vitest)

**kanban.test.ts** (3 tests)
- `moveCard` reorders within column
- `moveCard` moves between columns
- `moveCard` drops at column end

**KanbanBoard.test.tsx** (3 tests)
- Renders 5 columns on mount
- Column title rename
- Add and delete card flow

### E2E Tests (Playwright)

**kanban.spec.ts** (3 tests)
- Page loads and shows board
- Add card to column
- Drag and drop card between columns

### Test Status
✅ All 6 unit tests passing
✅ All 3 E2E tests passing

## Current Limitations

- In-memory state only (no persistence)
- No backend API integration
- No user authentication
- Fixed 5 columns (can be renamed but not added/removed)
- No AI chat integration
- Demo data only

## Next Steps (As Per Plan)

1. Will integrate with FastAPI backend
2. Will add user sign-in (hardcoded credentials)
3. Will persist board state to SQLite database
4. Will add AI chat sidebar with LLM integration
5. Will enable AI-driven card updates

## Development Commands

```bash
npm run dev          # Start dev server
npm run build        # Build for production
npm run start        # Start production server
npm test             # Run unit tests
npm run test:e2e     # Run Playwright tests
npm run test:all     # Run all tests
npm run lint         # Run ESLint
```
