import { render, screen, waitFor } from '@testing-library/react'
import { expect, test, vi } from 'vitest'
import { KnowledgeLibrary } from './KnowledgeLibrary'
import { ingestApi } from '../../lib/api-client'

// Mock API client
vi.mock('../../lib/api-client', () => ({
  ingestApi: {
    listFiles: vi.fn(),
    uploadFile: vi.fn(),
    deleteFile: vi.fn(),
    getStatus: vi.fn(),
  },
  chatApi: {
    streamChat: vi.fn(),
  },
  default: {
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    }
  }
}))

test('KnowledgeLibrary fetches and renders files on mount', async () => {
  const mockFiles = [
    { id: '1', filename: 'test1.pdf', status: 'completed', created_at: '2026-05-11T00:00:00Z' },
    { id: '2', filename: 'test2.txt', status: 'processing', created_at: '2026-05-11T00:01:00Z' },
  ]

  vi.mocked(ingestApi.listFiles).mockResolvedValue({ data: mockFiles, status: 200 } as any)

  render(<KnowledgeLibrary isOpen={true} onClose={() => {}} />)

  expect(screen.getByText('LocalRAG')).toBeDefined()
  expect(screen.getByText('Knowledge Assets')).toBeDefined()

  await waitFor(() => {
    expect(screen.getByText('test1.pdf')).toBeDefined()
    expect(screen.getByText('test2.txt')).toBeDefined()
  })
})
