#!/usr/bin/env python
"""
בדיקה מהירה של פונקציית התרגום
Quick test of translation function
"""

import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'branding_site.settings')
django.setup()

from main.utils import translate_hebrew_to_english_with_context
from django.conf import settings

def test_translation():
    print("🧪 בדיקת פונקציית התרגום...")
    
    # בדיקת מפתח API
    api_key = settings.OPENAI_API_KEY
    print(f"🔑 OPENAI_API_KEY length: {len(api_key)}")
    print(f"🔑 First 10 chars: {api_key[:10]}...")
    
    # בדיקת תרגום
    test_text = "בננה אחת"
    print(f"\n🔤 Testing translation of: '{test_text}'")
    
    try:
        result = translate_hebrew_to_english_with_context(test_text, None)
        print(f"✅ Translation result: '{result}'")
        
        if result == test_text:
            print("❌ ERROR: Translation returned same text - translation failed!")
        else:
            print("✅ SUCCESS: Translation worked!")
            
    except Exception as e:
        print(f"💥 ERROR in translation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_translation()
    print("\n🏁 Test completed!")
