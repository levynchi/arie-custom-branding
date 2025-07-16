#!/usr/bin/env python
import os
import django
from PIL import Image, ImageDraw, ImageFont
import io

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'branding_site.settings')
django.setup()

from main.models import Product
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

def create_dummy_image(text, filename, size=(400, 400), bg_color=(240, 240, 240), text_color=(100, 100, 100)):
    """יוצר תמונה דמה עם טקסט"""
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # נסה לטעון פונט, אם לא מצליח השתמש בפונט ברירת מחדל
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # חשב את מיקום הטקסט למרכז
    text_width = draw.textlength(text, font=font)
    text_height = 24  # גובה משוער של הפונט
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # צייר את הטקסט
    draw.text((x, y), text, fill=text_color, font=font)
    
    # שמור לבאפר
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return SimpleUploadedFile(filename, buffer.read(), content_type='image/png')

def add_images_to_products():
    """מוסיף תמונות דמה למוצרים"""
    products_without_images = Product.objects.filter(image='')
    
    for product in products_without_images:
        try:
            # יצירת תמונה דמה
            image_file = create_dummy_image(
                text=product.name,
                filename=f'{product.slug}.png',
                size=(400, 400)
            )
            
            # שמירת התמונה למוצר
            product.image.save(f'{product.slug}.png', image_file, save=True)
            print(f'נוצרה תמונה עבור: {product.name}')
            
        except Exception as e:
            print(f'שגיאה ביצירת תמונה עבור {product.name}: {e}')

if __name__ == '__main__':
    print("יצירת תמונות דמה עבור המוצרים...")
    add_images_to_products()
    print("הושלם!")
