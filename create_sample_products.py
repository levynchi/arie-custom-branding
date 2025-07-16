#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'branding_site.settings')
django.setup()

from main.models import Category, Product

def create_sample_data():
    print("יצירת מוצרי דמה...")
    
    # יצירת קטגוריות
    categories_data = [
        {'name': 'חולצות', 'slug': 'shirts', 'description': 'חולצות איכותיות למיתוג'},
        {'name': 'כובעים', 'slug': 'hats', 'description': 'כובעים לכל סוג של מיתוג'},
        {'name': 'תיקים', 'slug': 'bags', 'description': 'תיקים מותאמים אישית'},
        {'name': 'ספלים', 'slug': 'mugs', 'description': 'ספלים למיתוג חברתי'},
        {'name': 'הדפסות', 'slug': 'prints', 'description': 'הדפסות למיתוג'},
    ]

    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults={
                'name': cat_data['name'],
                'description': cat_data['description'],
                'is_active': True
            }
        )
        if created:
            print(f'נוצרה קטגוריה: {category.name}')

    # יצירת מוצרים
    products_data = [
        {
            'name': 'חולצת טי פולו',
            'slug': 'polo-shirt',
            'category': 'shirts',
            'description': 'חולצת פולו איכותית מכותנה 100% מתאימה למיתוג',
            'price': 89.90,
            'fabric_type': 'cotton',
            'colors_available': ['לבן', 'שחור', 'כחול', 'אדום'],
            'sizes_available': ['S', 'M', 'L', 'XL', 'XXL'],
            'stock_quantity': 50,
            'is_featured': True
        },
        {
            'name': 'חולצת טי רגילה',
            'slug': 't-shirt',
            'category': 'shirts',
            'description': 'חולצת טי בסיסית מכותנה איכותית',
            'price': 49.90,
            'fabric_type': 'cotton',
            'colors_available': ['לבן', 'שחור', 'אפור', 'כחול נייבי'],
            'sizes_available': ['S', 'M', 'L', 'XL'],
            'stock_quantity': 100,
            'is_featured': True
        },
        {
            'name': 'כובע מצחייה',
            'slug': 'baseball-cap',
            'category': 'hats',
            'description': 'כובע מצחייה קלאסי מתאים למיתוג',
            'price': 69.90,
            'fabric_type': 'cotton',
            'colors_available': ['שחור', 'כחול', 'אדום', 'לבן'],
            'sizes_available': ['One Size'],
            'stock_quantity': 30,
            'is_featured': True
        },
        {
            'name': 'כובע צמר',
            'slug': 'beanie',
            'category': 'hats',
            'description': 'כובע צמר חם ונוח לחורף',
            'price': 39.90,
            'fabric_type': 'blend',
            'colors_available': ['שחור', 'אפור', 'כחול'],
            'sizes_available': ['One Size'],
            'stock_quantity': 25
        },
        {
            'name': 'תיק קניות',
            'slug': 'shopping-bag',
            'category': 'bags',
            'description': 'תיק קניות אקולוגי מבד איכותי',
            'price': 29.90,
            'fabric_type': 'cotton',
            'colors_available': ['טבעי', 'שחור', 'כחול'],
            'sizes_available': ['רגיל'],
            'stock_quantity': 40
        },
        {
            'name': 'תיק גב',
            'slug': 'backpack',
            'category': 'bags',
            'description': 'תיק גב איכותי לעבודה ולטיולים',
            'price': 149.90,
            'fabric_type': 'polyester',
            'colors_available': ['שחור', 'כחול', 'אפור'],
            'sizes_available': ['רגיל'],
            'stock_quantity': 20,
            'is_featured': True
        },
        {
            'name': 'ספל קרמיקה',
            'slug': 'ceramic-mug',
            'category': 'mugs',
            'description': 'ספל קרמיקה איכותי למיתוג',
            'price': 19.90,
            'fabric_type': 'cotton',
            'colors_available': ['לבן', 'שחור', 'כחול', 'אדום'],
            'sizes_available': ['330ml'],
            'stock_quantity': 80,
            'is_featured': True
        },
        {
            'name': 'ספל נירוסטה',
            'slug': 'steel-mug',
            'category': 'mugs',
            'description': 'ספל נירוסטה איכותי לשמירה על חום',
            'price': 59.90,
            'fabric_type': 'cotton',
            'colors_available': ['כסף', 'שחור', 'כחול'],
            'sizes_available': ['400ml'],
            'stock_quantity': 35
        },
        {
            'name': 'הדפסה על בד',
            'slug': 'fabric-print',
            'category': 'prints',
            'description': 'הדפסה איכותית על בד לתליה',
            'price': 79.90,
            'fabric_type': 'polyester',
            'colors_available': ['צבעוני'],
            'sizes_available': ['30x40', '40x60', '60x80'],
            'stock_quantity': 15
        },
        {
            'name': 'הדפסה על נייר',
            'slug': 'paper-print',
            'category': 'prints',
            'description': 'הדפסה איכותית על נייר פוטו',
            'price': 29.90,
            'fabric_type': 'cotton',
            'colors_available': ['צבעוני'],
            'sizes_available': ['A4', 'A3', 'A2'],
            'stock_quantity': 60
        }
    ]

    for prod_data in products_data:
        try:
            category = Category.objects.get(slug=prod_data['category'])
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={
                    'name': prod_data['name'],
                    'category': category,
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'fabric_type': prod_data['fabric_type'],
                    'colors_available': prod_data['colors_available'],
                    'sizes_available': prod_data['sizes_available'],
                    'stock_quantity': prod_data['stock_quantity'],
                    'is_featured': prod_data.get('is_featured', False),
                    'is_active': True
                }
            )
            if created:
                print(f'נוצר מוצר: {product.name}')
        except Exception as e:
            print(f'שגיאה ביצירת מוצר {prod_data["name"]}: {e}')

    print('\nסיכום:')
    print(f'קטגוריות: {Category.objects.count()}')
    print(f'מוצרים: {Product.objects.count()}')
    print(f'מוצרים מומלצים: {Product.objects.filter(is_featured=True).count()}')

if __name__ == '__main__':
    create_sample_data()
