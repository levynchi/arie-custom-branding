#!/usr/bin/env python
"""
סקריפט לבדיקה ותיקון נתונים של AIConversation
Script to check and fix AIConversation data
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

from main.models import AIConversation
import uuid

def check_and_fix_conversations():
    """בדיקה ותיקון שיחות עם session_id ריק"""
    print("🔍 בדיקת נתונים של AIConversation...")
    
    # ספירת שיחות כללית
    total_conversations = AIConversation.objects.count()
    print(f"📊 סך הכל שיחות: {total_conversations}")
    
    # ספירת שיחות עם session_id ריק או NULL
    empty_session_conversations = AIConversation.objects.filter(
        models.Q(session_id__isnull=True) | models.Q(session_id='')
    )
    empty_count = empty_session_conversations.count()
    print(f"⚠️  שיחות עם session_id ריק: {empty_count}")
    
    if empty_count > 0:
        print("🔧 מתקן שיחות עם session_id ריק...")
        
        for conversation in empty_session_conversations:
            # יצירת session_id חדש
            new_session_id = str(uuid.uuid4())
            conversation.session_id = new_session_id
            conversation.save()
            
            user_info = conversation.user.username if conversation.user else "Anonymous"
            print(f"   ✅ תוקן: {user_info} - ID: {conversation.id} - Session: {new_session_id[:8]}...")
        
        print(f"🎉 תוקנו {empty_count} שיחות!")
    else:
        print("✅ כל השיחות תקינות!")
    
    # סטטיסטיקות נוספות
    authenticated_conversations = AIConversation.objects.filter(user__isnull=False).count()
    anonymous_conversations = AIConversation.objects.filter(user__isnull=True).count()
    
    print("\n📈 סטטיסטיקות:")
    print(f"👤 שיחות משתמשים מחוברים: {authenticated_conversations}")
    print(f"🕶️  שיחות משתמשים אנונימיים: {anonymous_conversations}")
    print(f"📱 סך הכל: {total_conversations}")

if __name__ == "__main__":
    from django.db import models
    check_and_fix_conversations()
    print("\n🏁 הסקריפט הסתיים בהצלחה!")
