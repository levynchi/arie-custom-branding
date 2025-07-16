#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'branding_site.settings')
django.setup()

from main.models import Category, Product

def create_textile_products():
    print("מחליף מוצרים במוצרי טקסטיל בלבד...")
    
    # מחיקת מוצרים קיימים
    Product.objects.all().delete()
    print("נמחקו מוצרים קיימים")
    
    # מחיקת קטגוריות קיימות
    Category.objects.all().delete()
    print("נמחקו קטגוריות קיימות")
    
    # יצירת קטגוריות טקסטיל
    categories_data = [
        {'name': 'חולצות', 'slug': 'shirts', 'description': 'חולצות איכותיות למיתוג - טי שירט, פולו, טנקטופ'},
        {'name': 'סווטשירטים', 'slug': 'sweatshirts', 'description': 'סווטשירטים וקפוצ\'ונים למיתוג'},
        {'name': 'כובעים', 'slug': 'hats', 'description': 'כובעים מכל הסוגים למיתוג'},
        {'name': 'תיקים', 'slug': 'bags', 'description': 'תיקים מבד למיתוג'},
        {'name': 'אביזרים', 'slug': 'accessories', 'description': 'אביזרי טקסטיל נוספים למיתוג'},
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

    # יצירת מוצרי טקסטיל
    products_data = [
        # חולצות
        {
            'name': 'חולצת טי שירט קלאסית',
            'slug': 't-shirt-classic',
            'category': 'shirts',
            'description': 'חולצת טי שירט קלאסית מכותנה 100% איכותית, מתאימה למיתוג בהדפסה או רקמה',
            'price': 45.00,
            'fabric_type': 'cotton',
            'colors_available': ['לבן', 'שחור', 'אפור', 'כחול נייבי', 'אדום', 'ירוק', 'צהוב'],
            'sizes_available': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
            'stock_quantity': 100,
            'is_featured': True
        },
        {
            'name': 'חולצת פולו איכותית',
            'slug': 'polo-shirt-premium',
            'category': 'shirts',
            'description': 'חולצת פולו איכותית מכותנה פיקה עם צווארון, מתאימה למיתוג עסקי',
            'price': 89.00,
            'fabric_type': 'cotton',
            'colors_available': ['לבן', 'שחור', 'כחול נייבי', 'אדום', 'אפור', 'ירוק כהה'],
            'sizes_available': ['S', 'M', 'L', 'XL', 'XXL'],
            'stock_quantity': 75,
            'is_featured': True
        },
        {
            'name': 'טנקטופ ספורט',
            'slug': 'tank-top-sport',
            'category': 'shirts',
            'description': 'טנקטופ ספורטיבי מבד נושם, מתאים לפעילות ספורט ומיתוג',
            'price': 35.00,
            'fabric_type': 'polyester',
            'colors_available': ['לבן', 'שחור', 'אפור', 'כחול', 'אדום'],
            'sizes_available': ['S', 'M', 'L', 'XL'],
            'stock_quantity': 60,
        },
        {
            'name': 'חולצת V צווארון',
            'slug': 'v-neck-shirt',
            'category': 'shirts',
            'description': 'חולצת טי שירט עם צווארון V, מתאימה למיתוג אלגנטי',
            'price': 52.00,
            'fabric_type': 'cotton',
            'colors_available': ['לבן', 'שחור', 'אפור', 'כחול נייבי'],
            'sizes_available': ['S', 'M', 'L', 'XL'],
            'stock_quantity': 45,
        },
        
        # סווטשירטים
        {
            'name': 'סווטשירט קלאסי',
            'slug': 'sweatshirt-classic',
            'category': 'sweatshirts',
            'description': 'סווטשירט קלאסי מכותנה ופוליאסטר, מתאים למיתוג עם רקמה או הדפסה',
            'price': 125.00,
            'fabric_type': 'blend',
            'colors_available': ['שחור', 'אפור', 'כחול נייבי', 'אדום', 'ירוק'],
            'sizes_available': ['S', 'M', 'L', 'XL', 'XXL'],
            'stock_quantity': 50,
            'is_featured': True
        },
        {
            'name': 'קפוצ\'ון עם כיס',
            'slug': 'hoodie-pocket',
            'category': 'sweatshirts',
            'description': 'קפוצ\'ון נוח עם כיס קנגורו, מתאים למיתוג מודרני',
            'price': 155.00,
            'fabric_type': 'blend',
            'colors_available': ['שחור', 'אפור', 'כחול נייבי', 'אדום'],
            'sizes_available': ['S', 'M', 'L', 'XL', 'XXL'],
            'stock_quantity': 40,
            'is_featured': True
        },
        {
            'name': 'ז\'קט ספורט',
            'slug': 'sport-jacket',
            'category': 'sweatshirts',
            'description': 'ז\'קט ספורט עם רוכסן, מתאים למיתוג ספורטיבי',
            'price': 185.00,
            'fabric_type': 'polyester',
            'colors_available': ['שחור', 'כחול נייבי', 'אפור', 'אדום'],
            'sizes_available': ['S', 'M', 'L', 'XL'],
            'stock_quantity': 30,
        },
        
        # כובעים
        {
            'name': 'כובע מצחייה קלאסי',
            'slug': 'baseball-cap-classic',
            'category': 'hats',
            'description': 'כובע מצחייה קלאסי מכותנה, מתאים למיתוג עם רקמה',
            'price': 65.00,
            'fabric_type': 'cotton',
            'colors_available': ['שחור', 'כחול נייבי', 'אדום', 'לבן', 'אפור'],
            'sizes_available': ['One Size'],
            'stock_quantity': 80,
            'is_featured': True
        },
        {
            'name': 'כובע צמר (ביני)',
            'slug': 'beanie-wool',
            'category': 'hats',
            'description': 'כובע צמר חם ונוח לחורף, מתאים לרקמה',
            'price': 45.00,
            'fabric_type': 'blend',
            'colors_available': ['שחור', 'אפור', 'כחול נייבי', 'אדום', 'ירוק'],
            'sizes_available': ['One Size'],
            'stock_quantity': 60,
        },
        {
            'name': 'כובע באקט',
            'slug': 'bucket-hat',
            'category': 'hats',
            'description': 'כובע באקט מבד, מתאים למיתוג קיצי',
            'price': 55.00,
            'fabric_type': 'cotton',
            'colors_available': ['חאכי', 'שחור', 'כחול נייבי', 'לבן'],
            'sizes_available': ['S/M', 'L/XL'],
            'stock_quantity': 35,
        },
        
        # תיקים
        {
            'name': 'תיק קניות בד',
            'slug': 'canvas-tote-bag',
            'category': 'bags',
            'description': 'תיק קניות אקולוגי מבד כותנה, מתאים להדפסה',
            'price': 35.00,
            'fabric_type': 'cotton',
            'colors_available': ['טבעי', 'שחור', 'כחול נייבי', 'אדום'],
            'sizes_available': ['רגיל', 'גדול'],
            'stock_quantity': 90,
            'is_featured': True
        },
        {
            'name': 'תיק גב טקסטיל',
            'slug': 'textile-backpack',
            'category': 'bags',
            'description': 'תיק גב מבד איכותי, מתאים למיתוג עסקי',
            'price': 165.00,
            'fabric_type': 'polyester',
            'colors_available': ['שחור', 'כחול נייבי', 'אפור'],
            'sizes_available': ['רגיל'],
            'stock_quantity': 25,
        },
        {
            'name': 'נרתיק לפלאפון',
            'slug': 'phone-pouch',
            'category': 'bags',
            'description': 'נרתיק טקסטיל לפלאפון, מתאים לרקמה',
            'price': 25.00,
            'fabric_type': 'cotton',
            'colors_available': ['שחור', 'כחול', 'אדום', 'ירוק'],
            'sizes_available': ['רגיל'],
            'stock_quantity': 70,
        },
        
        # אביזרים
        {
            'name': 'מגבת ספורט',
            'slug': 'sport-towel',
            'category': 'accessories',
            'description': 'מגבת ספורט מבד מיקרופייבר, מתאימה למיתוג',
            'price': 75.00,
            'fabric_type': 'polyester',
            'colors_available': ['לבן', 'כחול', 'אפור', 'ירוק'],
            'sizes_available': ['30x50', '50x100'],
            'stock_quantity': 40,
        },
        {
            'name': 'צעיף רך',
            'slug': 'soft-scarf',
            'category': 'accessories',
            'description': 'צעיף רך מבד איכותי, מתאים לרקמה עדינה',
            'price': 95.00,
            'fabric_type': 'cotton',
            'colors_available': ['שחור', 'אפור', 'כחול נייבי', 'אדום', 'ירוק'],
            'sizes_available': ['רגיל'],
            'stock_quantity': 30,
        },
        {
            'name': 'כפפות טקסטיל',
            'slug': 'textile-gloves',
            'category': 'accessories',
            'description': 'כפפות מבד חם לחורף, מתאימות לרקמה',
            'price': 42.00,
            'fabric_type': 'blend',
            'colors_available': ['שחור', 'אפור', 'כחול נייבי'],
            'sizes_available': ['S/M', 'L/XL'],
            'stock_quantity': 50,
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

    print('\nסיכום מוצרי טקסטיל:')
    print(f'קטגוריות: {Category.objects.count()}')
    print(f'מוצרים: {Product.objects.count()}')
    print(f'מוצרים מומלצים: {Product.objects.filter(is_featured=True).count()}')
    
    # פילוח לפי קטגוריות
    for category in Category.objects.all():
        count = Product.objects.filter(category=category).count()
        print(f'{category.name}: {count} מוצרים')

if __name__ == '__main__':
    create_textile_products()
