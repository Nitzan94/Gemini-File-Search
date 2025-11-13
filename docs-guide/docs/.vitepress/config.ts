import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Gemini File Search Guide',
  description: 'Interactive guide for building RAG applications with Google Gemini File Search API',

  locales: {
    root: {
      label: 'English',
      lang: 'en',
      themeConfig: {
        nav: [
          { text: 'Home', link: '/en/' },
          { text: 'Getting Started', link: '/en/getting-started/setup' },
          { text: 'Tutorial', link: '/en/tutorial/' },
          { text: 'API Reference', link: '/en/api/stores' }
        ],
        sidebar: {
          '/en/': [
            {
              text: 'Getting Started',
              collapsed: false,
              items: [
                { text: 'Setup', link: '/en/getting-started/setup' },
                { text: 'Create First Store', link: '/en/getting-started/first-store' },
                { text: 'First Query', link: '/en/getting-started/first-query' }
              ]
            },
            {
              text: 'Concepts',
              collapsed: false,
              items: [
                { text: 'Architecture', link: '/en/concepts/architecture' },
                { text: 'Stores', link: '/en/concepts/stores' },
                { text: 'Documents', link: '/en/concepts/documents' },
                { text: 'Semantic Search', link: '/en/concepts/semantic-search' },
                { text: 'Citations', link: '/en/concepts/citations' }
              ]
            },
            {
              text: 'Practical Guides',
              collapsed: false,
              items: [
                { text: 'Upload Documents', link: '/en/guides/upload-documents' },
                { text: 'Metadata Filtering', link: '/en/guides/metadata-filtering' },
                { text: 'FastAPI Integration', link: '/en/guides/fastapi-integration' },
                { text: 'Production Deployment', link: '/en/guides/production-deployment' }
              ]
            },
            {
              text: 'API Reference',
              collapsed: false,
              items: [
                { text: 'Stores', link: '/en/api/stores' },
                { text: 'Documents', link: '/en/api/documents' },
                { text: 'Query', link: '/en/api/query' }
              ]
            },
            {
              text: 'Troubleshooting',
              items: [
                { text: 'Common Issues', link: '/en/troubleshooting' }
              ]
            }
          ]
        }
      }
    },
    he: {
      label: 'עברית',
      lang: 'he',
      dir: 'rtl',
      themeConfig: {
        nav: [
          { text: 'דף הבית', link: '/he/' },
          { text: 'English Documentation', link: '/' }
        ],
        sidebar: {
          '/he/': [
            {
              text: 'בקרוב',
              items: [
                { text: 'התיעוד בעברית בפיתוח', link: '/he/' }
              ]
            }
          ]
        }
      }
    }
  },

  themeConfig: {
    logo: '/logo.svg',
    search: {
      provider: 'local'
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/Nitzan94/Gemini-File-Search' }
    ]
  },

  markdown: {
    config: (md) => {
      // Mermaid diagram support will be added via plugin
    }
  }
})
