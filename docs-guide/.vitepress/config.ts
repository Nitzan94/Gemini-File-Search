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
              text: 'Tutorial',
              items: [
                { text: 'Interactive Wizard', link: '/en/tutorial/' }
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
          { text: 'תחילת העבודה', link: '/he/getting-started/setup' },
          { text: 'מדריך אינטראקטיבי', link: '/he/tutorial/' },
          { text: 'תיעוד API', link: '/he/api/stores' }
        ],
        sidebar: {
          '/he/': [
            {
              text: 'תחילת העבודה',
              collapsed: false,
              items: [
                { text: 'התקנה והגדרה', link: '/he/getting-started/setup' },
                { text: 'יצירת מאגר ראשון', link: '/he/getting-started/first-store' },
                { text: 'שאילתה ראשונה', link: '/he/getting-started/first-query' }
              ]
            },
            {
              text: 'מושגי יסוד',
              collapsed: false,
              items: [
                { text: 'ארכיטקטורה', link: '/he/concepts/architecture' },
                { text: 'מאגרים', link: '/he/concepts/stores' },
                { text: 'מסמכים', link: '/he/concepts/documents' },
                { text: 'חיפוש סמנטי', link: '/he/concepts/semantic-search' },
                { text: 'ציטוטים', link: '/he/concepts/citations' }
              ]
            },
            {
              text: 'מדריכים מעשיים',
              collapsed: false,
              items: [
                { text: 'העלאת מסמכים', link: '/he/guides/upload-documents' },
                { text: 'סינון לפי מטא-דאטא', link: '/he/guides/metadata-filtering' },
                { text: 'אינטגרציה עם FastAPI', link: '/he/guides/fastapi-integration' },
                { text: 'פריסה לייצור', link: '/he/guides/production-deployment' }
              ]
            },
            {
              text: 'תיעוד API',
              collapsed: false,
              items: [
                { text: 'מאגרים', link: '/he/api/stores' },
                { text: 'מסמכים', link: '/he/api/documents' },
                { text: 'שאילתות', link: '/he/api/query' }
              ]
            },
            {
              text: 'מדריך אינטראקטיבי',
              items: [
                { text: 'אשף צעד-אחר-צעד', link: '/he/tutorial/' }
              ]
            },
            {
              text: 'פתרון בעיות',
              items: [
                { text: 'בעיות נפוצות', link: '/he/troubleshooting' }
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
