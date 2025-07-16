# אריה קאסטום מיתוגים - אתר מיתוג והדפסה

אתר Django מתקדם למיתוג והדפסה על מוצרי טקסטיל באיכות גבוהה.

## תכונות

- **עיצוב מודרני**: אתר רספונסיבי עם עיצוב מודרני וחדשני
- **עורך עיצובים**: עורך drag & drop מתקדם לעיצוב על מוצרים
- **קטלוג מוצרים**: מגוון רחב של מוצרי טקסטיל
- **ממשק ניהול**: פאנל ניהול מתקדם לניהול מוצרים וקטגוריות
- **תמיכה בעברית**: אתר מלא בעברית עם תמיכה RTL

## טכנולוגיות

- **Backend**: Django 5.2.4
- **Frontend**: Bootstrap 5.3.0, HTML5, CSS3, JavaScript
- **Database**: SQLite (ניתן לשדרג ל-PostgreSQL)
- **Icons**: Font Awesome 6.0.0
- **Language**: Python 3.10.4

## מוצרים

### קטגוריות
- חולצות (T-Shirts)
- סווטשירטים (Sweatshirts)  
- כובעים (Hats)
- תיקים (Bags)
- אביזרים (Accessories)

### מוצרים נתמכים
- חולצות קלאסיות
- חולצות V
- חולצות טנק
- פולו
- הודיז
- סווטשירטים
- כובעי בייסבול
- כובעי צמר
- כובעי דלי
- תיקי בד
- תיקי קניות
- תיקי גב
- כפפות
- צעיפים
- מגבות ספורט
- ועוד...

## התקנה

1. שכפל את הפרויקט:
```bash
git clone https://github.com/levynchi/arie-custom-branding.git
cd arie-custom-branding
```

2. צור סביבה וירטואלית:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. התקן dependencies:
```bash
pip install django pillow
```

4. הרץ migrations:
```bash
python manage.py migrate
```

5. צור superuser:
```bash
python manage.py createsuperuser
```

6. הרץ את השרת:
```bash
python manage.py runserver
```

## שימוש

1. **דף הבית**: `/` - דף הבית עם עיצוב מודרני
2. **מוצרים**: `/products/` - קטלוג מוצרים מלא
3. **קטגוריות**: `/category/<slug>/` - מוצרים לפי קטגוריה
4. **עיצוב**: `/design/` - עורך עיצובים אינטראקטיבי
5. **ניהול**: `/admin/` - פאנל ניהול Django

## תמיכה

לתמיכה נוספת או שאלות, פנה אלינו:
- WhatsApp: 050-123-4567
- Email: info@arie-custom.co.il

## רישיון

הפרויקט מוגן בזכויות יוצרים © 2025 אריה קאסטום מיתוגים
