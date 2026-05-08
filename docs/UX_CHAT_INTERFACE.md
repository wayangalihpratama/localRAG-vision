# UX Specification: LocalRAG Vision Chat Interface 🎨

## 1. Visual Identity & Rationale
- **Primary Color**: `#7C3AED` (Neon Violet) - *Chosen for its association with modern AI innovation and high-performance creativity.*
- **Typography**: Inter (Sans-serif) for high legibility.

### 🌗 Theme Support
The system must support dynamic theme switching using Tailwind 4 CSS variables.

| Feature | Dark Mode (Default) | Light Mode |
| :--- | :--- | :--- |
| **Background** | `#0F172A` (Deep Slate) | `#F8FAFC` (Ghost White) |
| **Surface** | `rgba(255, 255, 255, 0.05)` | `rgba(15, 23, 42, 0.05)` |
| **Text (Primary)**| `#F1F5F9` | `#1E293B` |
| **Accent** | Neon Violet | Deep Violet |

## 2. Core Components

### A. The Knowledge Library (Left Sidebar)
- **Document Cards**: Display filename, filetype icon, and sync status.
- **Progress Bars**: Dynamic violet bars showing `%` completion for extraction and indexing.
- **Action**: "Add New Document" button with drag-and-drop overlay.

### B. The Conversation Nexus (Center)
- **Message Bubbles**:
  - User: Minimalist violet outline.
  - AI: Glassmorphism surface with neon glow.
- **Citations**: Interactive badges `[1]`, `[2]` linking to source data.
- **Typing Indicator**: Animated "Analyzing sources..." state to provide feedback during retrieval latency.

### C. The Source Preview (Right Sidebar)
- **Active Context**: Displays the specific chunk or table retrieved for the current answer.
- **Markdown Support**: Renders tables and headers with high fidelity (Docling output).
- **Collapsible**: Can be hidden to maximize chat area.

## 3. Interaction Map
1. **Upload** -> Left Sidebar shows "Analyzing... 0%" -> Worker completes -> Status changes to "Synced".
2. **Search** -> Center shows "Analyzing sources..." -> AI responds with citations.
3. **Click Citation** -> Right Sidebar slides in with source text highlighted.
4. **Theme Toggle** -> Switch between Dark and Light modes without page reload, preserving state.

## 🖼️ UI Mockup
![LocalRAG Vision Mockup](./assets/dashboard_mockup.png)
