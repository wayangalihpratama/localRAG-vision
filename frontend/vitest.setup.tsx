import "@testing-library/jest-dom";
import { vi } from "vitest";
import React from "react";

// Global mock for lucide-react icons
vi.mock("lucide-react", () => ({
  Plus: () => <div />,
  MessageSquare: () => <div />,
  FileText: () => <div />,
  Settings: () => <div />,
  Send: () => <div />,
  Sidebar: () => <div />,
  ChevronRight: () => <div />,
  Loader2: () => <div />,
  Database: () => <div />,
  Search: () => <div />,
  Upload: () => <div />,
  Trash2: () => <div />,
  X: () => <div />,
  Check: () => <div />,
  AlertCircle: () => <div />,
  Menu: () => <div />,
}));

// Global mock for fetch
global.fetch = vi.fn();

// Global mock for axios
vi.mock("axios", () => {
  return {
    default: {
      create: vi.fn().mockReturnValue({
        get: vi.fn().mockResolvedValue({ data: [] }),
        post: vi.fn().mockResolvedValue({ data: {} }),
        delete: vi.fn().mockResolvedValue({ data: {} }),
        interceptors: {
          request: { use: vi.fn(), eject: vi.fn() },
          response: { use: vi.fn(), eject: vi.fn() },
        },
      }),
    },
  };
});
