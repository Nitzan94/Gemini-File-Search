---
layout: home

hero:
  name: Gemini File Search
  text: בניית יישומי RAG
  tagline: מדריך אינטר אקטיבי ל-API של Google Gemini File Search - חיפוש סמנטי עם ציטוטים, ללא חלוקה ידנית
  image:
    src: /logo.svg
    alt: Gemini File Search
  actions:
    - theme: brand
      text: תחילת העבודה
      link: /he/getting-started/setup
    - theme: alt
      text: מדריך אינטראקטיבי
      link: /he/tutorial/
    - theme: alt
      text: תיעוד API
      link: /he/api/stores

features:
  - icon: 🔍
    title: חיפוש סמנטי
    details: שאילתות בשפה טבעית על פני המסמכים שלך עם הבנה מבוססת AI
  - icon: 📚
    title: 100+ פורמטי קבצים
    details: PDF, DOCX, קבצי קוד, גיליונות אלקטרוניים ועוד - העלה וחפש בכולם
  - icon: 🎯
    title: ציטוטים ממקור
    details: כל תשובה כוללת ציטוטים המראים בדיוק מאיפה המידע הגיע
  - icon: ⚡
    title: תשתית מנוהלת
    details: ללא חלוקה ידנית או הטמעות - Gemini מטפל בהכל אוטומטית
  - icon: 🔐
    title: סינון לפי מטא-דאטא
    details: סנן חיפושים לפי מטא-דאטא מותאם אישית (מחבר, תאריך, קטגוריה וכו')
  - icon: 🚀
    title: אינטגרציה עם FastAPI
    details: תבניות מוכנות לייצור לבניית יישומי אינטרנט

---

## למה Gemini File Search?

**מערכות RAG מסורתיות** דורשות ממך באופן ידני:
- לחלק מסמכים לחלקים
- ליצור הטמעות (embeddings)
- לנהל מסדי נתונים וקטוריים
- לכוונן אסטרטגיות חלוקה

**Gemini File Search** מטפל בכל זה אוטומטית. פשוט העלה קבצים והתחל לשאול שאילתות.

## דוגמה מהירה

```python
from google import genai

# אתחול
client = genai.Client(api_key='YOUR_KEY')

# יצירת מאגר
store = client.file_search_stores.create(
    config={'display_name': 'המסמכים שלי'}
)

# העלאת מסמך
operation = client.file_search_stores.upload_to_file_search_store(
    file='report.pdf',
    file_search_store_name=store.name
)

# שאילתה עם ציטוטים
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='מה היו ההכנסות ברבעון השני?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name]
            )
        )]
    )
)

print(response.text)  # תשובת AI עם ציטוטים
```

## מה תלמד

- **תחילת העבודה**: התקנה, מפתחות API, שאילתה ראשונה (10 דקות)
- **מושגי יסוד**: ארכיטקטורה, מאגרים, מסמכים, חיפוש (20 דקות)
- **אינטגרציה**: תבניות FastAPI, פריסה לייצור (30 דקות)
- **מתקדם**: סינון מטא-דאטא, פתרון בעיות, אופטימיזציה (20 דקות)

## מוכן להתחיל?

<div style="display: flex; gap: 1rem; margin-top: 2rem; direction: rtl;">
  <a href="/he/getting-started/setup" style="padding: 0.75rem 1.5rem; background: #4285f4; color: white; border-radius: 8px; text-decoration: none; font-weight: 500;">
    📖 קרא את המדריך
  </a>
  <a href="/he/tutorial/" style="padding: 0.75rem 1.5rem; border: 2px solid #4285f4; color: #4285f4; border-radius: 8px; text-decoration: none; font-weight: 500;">
    🎓 עבור את ההדרכה
  </a>
</div>

## משאבים

- [תיעוד Gemini הרשמי](https://ai.google.dev/gemini-api/docs/file-search)
- [קבל מפתח API](https://aistudio.google.com/apikey)
- [מאגר GitHub](https://github.com/Nitzan94/Gemini-File-Search)
- [Python SDK](https://github.com/googleapis/python-genai)
