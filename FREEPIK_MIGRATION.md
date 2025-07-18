# מיגרציה ל-Freepik AI API

## סקירה כללית
ברנץ' זה מכיל גירסה חדשה של מערכת הגנרציה שמשתמשת ב-Freepik AI API במקום Stability AI.

## שינויים עיקריים

### 1. החלפת ספק AI
- **לפני**: Stability AI (Stable Diffusion XL)
- **אחרי**: Freepik AI Text-to-Image API

### 2. שינויים בקוד
- `main/views.py`: עודכן לעבוד עם Freepik API
- `branding_site/settings.py`: הוספת הגדרות Freepik API
- `.env`: הוספת משתנה `FREEPIK_API_KEY`

### 3. שינויים ב-API Calls
- **Endpoint**: `https://api.freepik.com/v1/ai/text-to-image`
- **Headers**: `X-Freepik-API-Key` במקום `Authorization: Bearer`
- **Response Format**: JSON עם מערך `data` במקום `artifacts`

## הגדרת API Key

1. השג API Key מ-Freepik:
   - עבור לאתר Freepik Developers
   - צור חשבון ואשר אותו
   - צור API Key חדש

2. עדכן את קובץ `.env`:
   ```
   FREEPIK_API_KEY=your_actual_freepik_api_key_here
   ```

## מה נשמר
- כל הפונקציונליות של תרגום עברית-אנגלית (OpenAI)
- פונקציית יצירת SVG לטקסטים
- עיבוד תמונות (הסרת רקע, CMYK, 300 DPI)
- כל התכונות הקיימות נשמרו

## מה השתנה
- שם הקבצים: `freepik_design_` במקום `ai_design_`
- הודעות דיבוג: מציינות "Freepik AI"
- טיפול בשגיאות מותאם ל-Freepik API format

## גלבק לגירסה הקודמת
אם יש בעיות עם Freepik API:

```bash
git checkout master
```

זה יחזיר אותך לגירסה היציבה עם Stability AI.

## בדיקה
1. וודא שה-API Key של Freepik תקין
2. נסה ליצור עיצוב פשוט
3. בדוק שהתמונות נשמרות כראוי
4. וודא שהתרגום עברית-אנגלית עדיין עובד

## הערות טכניות
- Freepik API עשוי להיות יותר יציב מ-Stability AI
- איכות התמונות עשויה להיות שונה
- זמני תגובה עשויים להשתנות
- יש להתאים את הפרומפטים לפי הצורך
