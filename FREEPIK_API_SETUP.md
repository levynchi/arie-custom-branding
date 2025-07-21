# הגדרת Freepik API למאגר התמונות

## צעדים לקבלת מפתח API של Freepik:

### 1. יצירת חשבון
1. לך ל-https://www.freepik.com/developers/dashboard/api-key
2. צור חשבון חדש או התחבר עם חשבון קיים
3. אמת את המייל שלך

### 2. יצירת מפתח API
1. בדף ה-Dashboard לחץ על "Create API Key"
2. תן שם למפתח (למשל: "Custom Design Tool")
3. העתק את המפתח שנוצר

### 3. הגדרה במערכת
יש שתי דרכים להגדיר את המפתח:

#### דרך 1: משתנה סביבה (מומלץ)
```bash
set FREEPIK_API_KEY=your_actual_api_key_here
```

#### דרך 2: עדכון ישירות ב-settings.py
```python
# ב-branding_site/settings.py
FREEPIK_API_KEY = 'your_actual_api_key_here'
```

### 4. בדיקת התקנה
1. הפעל את השרת: `python manage.py runserver`
2. לך לדף העיצוב המותאם
3. נסה לחפש תמונות (למשל: "banana" או "dog")
4. אמור לקבל תוצאות מ-Freepik

## קרדיטים וחיובים
- חשבון חדש מקבל 5$ קרדיט חינמי
- כל חיפוש וגישה לתמונה חורגת מהקרדיט
- תוכל לעקוב אחר השימוש ב-Dashboard

## Fallback APIs
אם Freepik לא עובד, המערכת עוברת אוטומטית ל:
1. Unsplash (חינם לגמרי)
2. תמונות placeholder

## פרטים טכניים
- API Endpoint: https://api.freepik.com/v1/resources
- Authentication: Header `x-freepik-api-key`
- מגבלות: לפי תוכנית המנוי
- תיעוד מלא: https://docs.freepik.com/

## בעיות נפוצות

### שגיאה 401
- מפתח API לא תקין או לא הוגדר
- בדוק את המפתח ב-Dashboard

### שגיאה 403
- נגמרו הקרדיטים
- צריך לשדרג את התוכנית או לחכות לחידוש

### שגיאה 400
- פרמטרים שגויים בבקשה
- בדוק את format הבקשה בקוד
