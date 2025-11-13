# Gemini File Search - Interactive Guide

Interactive bilingual (English/Hebrew) documentation for the Gemini File Search API.

## Features

- ✅ **VitePress** - Modern, fast documentation framework
- ✅ **Bilingual** - English & Hebrew with full RTL support
- ✅ **Interactive Components**:
  - CodePlayground: Syntax-highlighted code with copy button
  - InteractiveDiagram: Clickable Mermaid diagrams
  - TutorialWizard: Step-by-step guided tutorials
  - VideoPlayer: GIF/MP4 support with captions
- ✅ **Full-text Search** - Built-in local search
- ✅ **Responsive** - Mobile-friendly design

## Quick Start

```bash
# Install dependencies
npm install

# Start dev server
npm run docs:dev
# Opens at http://localhost:5173/

# Build for production
npm run docs:build

# Preview production build
npm run docs:preview
```

## Project Structure

```
docs-guide/
├── docs/
│   ├── en/                      # English content
│   │   ├── index.md            # ✅ Home page (completed)
│   │   ├── getting-started/
│   │   │   ├── setup.md        # ✅ Setup guide (completed)
│   │   │   ├── first-store.md  # ⏳ TODO
│   │   │   └── first-query.md  # ⏳ TODO
│   │   ├── concepts/
│   │   │   ├── architecture.md # ✅ With diagrams (completed)
│   │   │   ├── stores.md       # ⏳ TODO
│   │   │   ├── documents.md    # ⏳ TODO
│   │   │   ├── semantic-search.md # ⏳ TODO
│   │   │   └── citations.md    # ⏳ TODO
│   │   ├── guides/
│   │   │   ├── upload-documents.md        # ⏳ TODO
│   │   │   ├── metadata-filtering.md      # ⏳ TODO
│   │   │   ├── fastapi-integration.md     # ⏳ TODO
│   │   │   └── production-deployment.md   # ⏳ TODO
│   │   ├── api/
│   │   │   ├── stores.md       # ⏳ TODO (with live examples)
│   │   │   ├── documents.md    # ⏳ TODO
│   │   │   └── query.md        # ⏳ TODO
│   │   ├── tutorial/
│   │   │   └── index.md        # ✅ Interactive wizard (completed)
│   │   └── troubleshooting.md  # ⏳ TODO
│   └── he/                      # Hebrew translations
│       └── [mirror en/ structure] # ⏳ TODO
├── .vitepress/
│   ├── config.ts               # ✅ i18n config (completed)
│   └── theme/
│       ├── index.ts            # ✅ Theme setup (completed)
│       ├── components/         # ✅ All 4 components (completed)
│       │   ├── CodePlayground.vue
│       │   ├── InteractiveDiagram.vue
│       │   ├── TutorialWizard.vue
│       │   └── VideoPlayer.vue
│       └── styles/
│           ├── index.css       # ✅ Main styles (completed)
│           └── rtl.css         # ✅ RTL support (completed)
└── package.json
```

## Content Status

### ✅ Completed (3 pages + all components)

1. **Home Page** (`en/index.md`)
   - Hero section with quick links
   - Features overview
   - Quick code example
   - Resources

2. **Setup Guide** (`en/getting-started/setup.md`)
   - Installation instructions
   - API key setup
   - Connection testing
   - Common issues
   - Complete example

3. **Architecture** (`en/concepts/architecture.md`)
   - Interactive diagrams (4)
   - System components
   - Data flow
   - Storage tiers
   - Integration patterns

4. **Interactive Tutorial** (`en/tutorial/index.md`)
   - 5-step wizard with TutorialWizard component
   - Hands-on examples
   - Task validation
   - Progress tracking

### ⏳ TODO - English Content (15 pages)

**Getting Started** (2 pages):
- `first-store.md` - Create and manage stores
- `first-query.md` - Upload docs and run first query

**Concepts** (4 pages):
- `stores.md` - Deep dive into stores
- `documents.md` - Document lifecycle, states, formats
- `semantic-search.md` - How search works, relevance
- `citations.md` - Citation extraction, grounding metadata

**Guides** (4 pages):
- `upload-documents.md` - Upload patterns, validation, monitoring
- `metadata-filtering.md` - Custom metadata, AIP-160 syntax, examples
- `fastapi-integration.md` - Complete FastAPI integration from DEVELOPER_GUIDE.md
- `production-deployment.md` - Docker, env vars, monitoring

**API Reference** (3 pages):
- `stores.md` - Store CRUD with live Sandpack examples
- `documents.md` - Document operations with examples
- `query.md` - Search API with live playground

**Troubleshooting** (1 page):
- `troubleshooting.md` - From existing troubleshooting.md

**Other** (1 page):
- Add logo at `/docs/public/logo.svg`

### ⏳ TODO - Hebrew Translation (ALL pages)

Translate all English content to Hebrew:
- Use proper Hebrew terminology
- Right-to-left text flow
- Keep code blocks LTR
- Test RTL layout

### ⏳ TODO - Media Assets

Create GIF/MP4 files:
- Upload flow demo (GIF, ~10s)
- Chat interface demo (GIF, ~15s)
- Document states animation (GIF, ~10s)
- Complete workflow (MP4, ~2min)
- Architecture explanation (MP4, ~1.5min)

Store in `/docs/public/media/` and reference with:
```vue
<VideoPlayer
  src="/media/upload-demo.gif"
  type="gif"
  caption="Drag and drop file upload"
/>
```

## Using Interactive Components

### CodePlayground

```vue
<CodePlayground
  title="Example Title"
  :code="`your code here`"
  language="python"
  :live="false"
/>
```

**Props**:
- `title`: Display title
- `code`: Code content (use backticks)
- `language`: `python`, `javascript`, `bash`
- `live`: `true` for Sandpack playground, `false` for read-only

### InteractiveDiagram

```vue
<InteractiveDiagram
  title="Optional Title"
  description="Optional description"
  :chart="`graph TB
    A[Start] --> B[End]
  `"
/>
```

**Uses Mermaid syntax**. See [Mermaid docs](https://mermaid.js.org/).

### TutorialWizard

```vue
<TutorialWizard
  :steps="[
    {
      title: 'Step 1',
      content: '<p>HTML content</p>',
      code: 'optional code',
      language: 'python',
      task: 'Optional task for user'
    }
  ]"
  :requireCompletion="false"
/>
```

### VideoPlayer

```vue
<VideoPlayer
  src="/media/demo.gif"
  type="gif"
  caption="Demo animation"
/>
```

## Content Guidelines

### Writing Style
- Concise, direct language
- Short sentences
- Action-oriented headings
- Code examples for every concept

### Code Examples
- Always working, runnable code
- Include comments
- Show expected output
- Handle errors

### Diagrams
- Use Mermaid for flows, sequences, states
- Keep diagrams focused (one concept)
- Add descriptions

### Hebrew Translation Tips
- Technical terms: Keep English in parentheses first time
- Example: "מאגר (Store)"
- Direction: RTL for text, LTR for code
- Test: View in browser, check alignment

## Building Content

### Quick Template for New Page

```md
# Page Title

Brief introduction (1-2 sentences).

## Section 1

Content here.

<CodePlayground
  title="Example"
  :code="`python code`"
  language="python"
/>

## What You've Learned

- Point 1
- Point 2

## Next Steps

- [Link to next page](/path)
```

### Content Sources

Use these existing docs as sources:
- `../DEVELOPER_GUIDE.md` - Technical details, patterns
- `../.claude/skills/gemini-file-search/SKILL.md` - Core workflow
- `../.claude/skills/gemini-file-search/references/*.md` - API reference, troubleshooting

## Deployment

### Option 1: Vercel

```bash
npm run docs:build
# Deploy dist/ folder to Vercel
```

### Option 2: GitHub Pages

```bash
# Add to .github/workflows/deploy.yml
npm run docs:build
# Publish docs/.vitepress/dist to gh-pages branch
```

### Option 3: FastAPI Integration

```python
# In main.py
from fastapi.staticfiles import StaticFiles

app.mount("/guide", StaticFiles(directory="docs-guide/docs/.vitepress/dist", html=True))
```

## Testing

### Test Locally
1. Run `npm run docs:dev`
2. Open http://localhost:5173/
3. Test English pages: http://localhost:5173/en/
4. Test Hebrew pages: http://localhost:5173/he/ (when ready)
5. Check RTL layout in Hebrew
6. Test search functionality
7. Test interactive components
8. Mobile responsive

### Test Production Build
```bash
npm run docs:build
npm run docs:preview
```

## Current Status

**Completed**: 25% (Foundation + 3 key pages + all components)
**Remaining**:
- English content: 15 pages (~8-10 hours)
- Hebrew translation: All pages (~6-8 hours)
- Media assets: 5 videos/GIFs (~2-3 hours)
- Testing & polish: ~2 hours

**Estimated Time to Complete**: 18-23 hours

## Getting Help

- **VitePress Docs**: https://vitepress.dev/
- **Mermaid Docs**: https://mermaid.js.org/
- **Vue 3 Docs**: https://vuejs.org/
- **Sandpack Docs**: https://sandpack.codesandbox.io/

## Notes

- All components are Vue 3 with TypeScript
- Mermaid diagrams support dark mode automatically
- RTL CSS tested for Hebrew layout
- Search is fully functional with local provider
- Build output is static HTML/CSS/JS (can deploy anywhere)
