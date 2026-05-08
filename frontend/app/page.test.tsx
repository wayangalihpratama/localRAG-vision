import { render, screen } from '@testing-library/react'
import { expect, test, vi } from 'vitest'
import Dashboard from './page'

// Mock icons to avoid rendering complexity in unit tests
vi.mock('lucide-react', () => ({
  Plus: () => <div data-testid="plus-icon" />,
  MessageSquare: () => <div />,
  FileText: () => <div />,
  Settings: () => <div />,
  Send: () => <div />,
  Sidebar: () => <div />,
  ChevronRight: () => <div />,
  Loader2: () => <div />,
  Database: () => <div />,
  Search: () => <div />,
}))

test('Dashboard renders the branding title', () => {
  render(<Dashboard />)
  expect(screen.getByText('LocalRAG')).toBeDefined()
})

test('Dashboard has a New Chat button', () => {
  render(<Dashboard />)
  expect(screen.getByText('New Chat')).toBeDefined()
})
