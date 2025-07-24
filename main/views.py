from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.utils import timezone
import json
import requests
import base64
import os
import uuid
import time
from datetime import datetime
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image
import io
from .models import Category, Product, BusinessQuote, CustomDesign, AIConversation, AIMessage
from .forms import BusinessQuoteForm, ContactForm
from .utils import (
    translate_hebrew_to_english, 
    translate_hebrew_to_english_with_context,
    clean_prompt_for_ai, 
    create_freepik_payload, 
    send_flux_request,
    get_or_create_session_id
)

def home(request):
    """דף הבית עם מוצרים מומלצים וקטגוריות"""
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:6]
    categories = Category.objects.filter(is_active=True)[:8]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'main/home.html', context)

def category_products(request, category_slug):
    """דף קטגוריה המציג את כל המוצרים באותה קטגוריה"""
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    products_list = Product.objects.filter(category=category, is_active=True)
    
    # Search functionality within category
    search_query = request.GET.get('search')
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filter by fabric type
    fabric_type = request.GET.get('fabric')
    if fabric_type:
        products_list = products_list.filter(fabric_type=fabric_type)
    
    # Get available fabric types for this category
    fabric_types = products_list.values_list('fabric_type', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': products,
        'fabric_types': fabric_types,
        'search_query': search_query,
        'selected_fabric': fabric_type,
    }
    return render(request, 'main/category_products.html', context)

def products(request):
    """עמוד המוצרים עם סינון וחיפוש"""
    products_list = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        products_list = products_list.filter(category__slug=category_slug)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filter by fabric type
    fabric_type = request.GET.get('fabric')
    if fabric_type:
        products_list = products_list.filter(fabric_type=fabric_type)
    
    # Pagination
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
        'fabric_choices': Product.FABRIC_CHOICES,
        'current_fabric': fabric_type,
    }
    return render(request, 'main/products.html', context)

def product_detail(request, slug):
    """עמוד פרטי מוצר"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'main/product_detail.html', context)

def business_quote(request):
    """עמוד בקשת הצעת מחיר לעסקים"""
    if request.method == 'POST':
        form = BusinessQuoteForm(request.POST, request.FILES)
        if form.is_valid():
            quote = form.save()
            messages.success(request, 'הבקשה נשלחה בהצלחה! נחזור אליך בהקדם.')
            
            # Send email notification (optional)
            try:
                send_mail(
                    subject=f'בקשת הצעת מחיר חדשה מ-{quote.company_name}',
                    message=f'התקבלה בקשה חדשה מ-{quote.company_name}\nאיש קשר: {quote.contact_person}\nטלפון: {quote.phone}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except:
                pass
            
            return render(request, 'main/business_quote_success.html')
    else:
        form = BusinessQuoteForm()
    
    context = {
        'form': form,
    }
    return render(request, 'main/business_quote.html', context)

def about(request):
    """עמוד אודות"""
    return render(request, 'main/about.html')

def contact(request):
    """עמוד יצירת קשר"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Send email
            try:
                send_mail(
                    subject=f'הודעה מהאתר: {subject}',
                    message=f'שם: {name}\nאימייל: {email}\n\n{message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
                messages.success(request, 'ההודעה נשלחה בהצלחה!')
            except:
                messages.error(request, 'אירעה שגיאה בשליחת ההודעה. אנא נסה שוב.')
            
            return render(request, 'main/contact.html', {'form': ContactForm()})
    else:
        form = ContactForm()
    
    context = {
        'form': form,
    }
    return render(request, 'main/contact.html', context)

def custom_design(request):
    """דף עיצוב אישי"""
    import time
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # בדיקה אם יש מוצר נבחר מראש
    selected_product_id = request.GET.get('product')
    selected_product = None
    if selected_product_id:
        try:
            selected_product = Product.objects.get(id=selected_product_id, is_active=True)
        except Product.DoesNotExist:
            pass
    
    context = {
        'products': products,
        'categories': categories,
        'selected_product': selected_product,
        'current_time': int(time.time()),  # Cache busting
    }
    return render(request, 'main/custom_design.html', context)

@csrf_exempt
def save_design(request):
    """שמירת עיצוב אישי"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            design_name = data.get('name', 'עיצוב ללא שם')
            design_data = data.get('design_data', {})
            
            # Get selected product if exists
            product = None
            product_data = design_data.get('product')
            if product_data and product_data.get('id'):
                try:
                    product = Product.objects.get(id=product_data['id'])
                except Product.DoesNotExist:
                    pass
            
            # If user is authenticated, save to database
            if request.user.is_authenticated:
                design = CustomDesign.objects.create(
                    user=request.user,
                    product=product,
                    name=design_name,
                    design_data=design_data
                )
                return JsonResponse({'success': True, 'design_id': design.id})
            else:
                # For anonymous users, return success but don't save
                return JsonResponse({'success': True, 'message': 'להרשמה כדי לשמור עיצובים'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'שיטה לא תקינה'})

@csrf_exempt
def generate_ai_design(request):
    """יצירת עיצוב באמצעות AI עם תמיכה בהיסטוריית שיחה ותמונת סטייל"""
    if request.method == 'POST':
        try:
            # Handle both JSON data and multipart form data (for file uploads)
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Handle file upload case
                prompt = request.POST.get('prompt', '')
                product_id = request.POST.get('product_id', '')
                product_name = request.POST.get('product_name', '')
                conversation_id = request.POST.get('conversation_id', None)
                style_image = request.FILES.get('style_image', None)
                base_image_url = request.POST.get('base_image_url', None)  # תמונה לעריכה
            else:
                # Handle JSON case
                data = json.loads(request.body)
                prompt = data.get('prompt', '')
                product_id = data.get('product_id', '')
                product_name = data.get('product_name', '')
                conversation_id = data.get('conversation_id', None)
                style_image = None
                base_image_url = data.get('base_image_url', None)  # תמונה לעריכה
            
            print(f"📥 DEBUG: POST request received")
            print(f"📥 DEBUG: prompt: '{prompt}'")
            print(f"📥 DEBUG: product_id: {product_id}")
            print(f"📥 DEBUG: conversation_id: {conversation_id}")
            print(f"📥 DEBUG: style_image: {'Uploaded' if style_image else 'None'}")
            print(f"📥 DEBUG: base_image_url: {base_image_url if base_image_url else 'None'}")
            
            if not prompt:
                return JsonResponse({'success': False, 'error': 'חסר תיאור עיצוב'})
            
            # Validate product_id if provided
            product = None
            if product_id:
                try:
                    product = Product.objects.get(id=product_id, is_active=True)
                    print(f"✅ DEBUG: Found product: {product.name}")
                except Product.DoesNotExist:
                    print(f"❌ DEBUG: Product with ID {product_id} not found")
                    product_id = None  # Reset to None if product doesn't exist
            
            # Get session ID for all users (authenticated and anonymous)
            session_id = get_or_create_session_id(request)
            print(f"🔑 DEBUG: Session ID: {session_id}")
            
            # Get or create conversation
            conversation = None
            print(f"🔍 DEBUG: conversation_id parameter: {conversation_id}")
            if conversation_id:
                # Try to get existing conversation
                try:
                    if request.user.is_authenticated:
                        conversation = AIConversation.objects.get(
                            id=conversation_id, 
                            user=request.user
                        )
                    else:
                        conversation = AIConversation.objects.get(
                            id=conversation_id,
                            session_id=session_id,
                            user__isnull=True
                        )
                except AIConversation.DoesNotExist:
                    conversation = None
            
            # Create new conversation if none exists
            if not conversation:
                # Set title based on first prompt (truncated)
                title = prompt[:50] + "..." if len(prompt) > 50 else prompt
                conversation = AIConversation.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    session_id=session_id,  # כל המשתמשים יקבלו session_id
                    product=product,  # Use the validated product object instead of product_id
                    title=title
                )
                print(f"🆕 DEBUG: Created NEW conversation {conversation.id}")
            else:
                print(f"🔄 DEBUG: Using EXISTING conversation {conversation.id}")
            
            # Save user message
            user_message = AIMessage.objects.create(
                conversation=conversation,
                message_type='user',
                content=prompt
            )
            
            # Get product dimensions if product exists
            max_width = 396.8  # Default width in pixels
            max_height = 453.5  # Default height in pixels
            
            if product:
                if product.can_print and product.max_print_width and product.max_print_height:
                    # Convert cm to pixels at 300 DPI
                    # 1 cm = 300/2.54 pixels at 300 DPI ≈ 118.11 pixels
                    cm_to_pixels_300dpi = 300 / 2.54
                    max_width = product.max_print_width * cm_to_pixels_300dpi
                    max_height = product.max_print_height * cm_to_pixels_300dpi
                    product_name = product.name
                    # Update conversation product if not set
                    if not conversation.product:
                        conversation.product = product
                        conversation.save()
            
            # Build very simple prompt for accurate results - translate Hebrew to English with context
            simple_prompt = prompt.strip()
            print(f"🔍 DEBUG: Original prompt from user: '{prompt}'")
            print(f"🔍 DEBUG: Cleaned prompt: '{simple_prompt}'")
            print(f"🔄 DEBUG: Using conversation ID: {conversation.id}")
            
            print("🚀 DEBUG: Starting translation process...")
            
            # Try to translate Hebrew to English using the utils function with context
            print(f"📤 DEBUG: Sending to OpenAI for translation with context: '{simple_prompt}'")
            print("=" * 50)
            print("📤 OPENAI REQUEST:")
            print(f"Input text: '{simple_prompt}'")
            print(f"Conversation context: {conversation.messages.count()} messages")
            print("=" * 50)
            
            print("🔍 DEBUG: About to call translate_hebrew_to_english_with_context...")
            try:
                enhanced_prompt = translate_hebrew_to_english_with_context(simple_prompt, conversation)
                print("🔍 DEBUG: translate_hebrew_to_english_with_context returned!")
            except Exception as translation_error:
                print(f"💥 DEBUG: Translation failed with error: {str(translation_error)}")
                print("🔄 DEBUG: Using original prompt instead")
                enhanced_prompt = simple_prompt
            
            print("=" * 50)
            print("📥 OPENAI RESPONSE:")
            print(f"Original: '{simple_prompt}'")
            print(f"Translated: '{enhanced_prompt}'")
            print("=" * 50)
            
            print(f"✅ DEBUG: Final translated prompt: '{enhanced_prompt}'")
            
            # בדיקה אם יש שינוי בפועל
            if enhanced_prompt == simple_prompt:
                print("⚠️ DEBUG: WARNING - Translation returned same text! Translation may have failed.")
            else:
                print("✅ DEBUG: Translation successful - text changed.")
            
            # בדיקה אם המשתמש שלח תמונה לעריכה באופן מפורש
            is_image_edit_request = bool(base_image_url)
            
            # זיהוי אם זה עריכת צבע - הרחבת הרשימה לכיסוי יותר מקרים
            color_keywords = ['אדום', 'אדומה', 'כחול', 'כחולה', 'ירוק', 'ירוקה', 'צהוב', 'צהובה', 'סגול', 'סגולה', 'כתום', 'כתומה', 'ורוד', 'ורודה', 'שחור', 'שחורה', 'לבן', 'לבנה', 'חום', 'חומה', 'אפור', 'אפורה',
                            'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'black', 'white', 'brown', 'gray',
                            'יותר אדום', 'more red', 'צבע', 'color', 'לצבוע', 'paint', 'הפוך', 'תעשה', 'בצבע', 'צבעי',
                            'בלי צהוב', 'without yellow', 'make it', 'change color',
                            'turn', 'transform', 'recolor', 'darker', 'lighter', 'brighter', 'בננה אדומה', 'בננה כחולה', 'בננה ירוקה']
            is_color_edit_request = any(color in prompt.lower() for color in color_keywords) and is_image_edit_request
            
            # דבאגינג לזיהוי צבעים
            if is_image_edit_request:
                found_colors = [color for color in color_keywords if color in prompt.lower()]
                print(f"🔍 DEBUG: Found color keywords: {found_colors}")
            
            print(f"🎯 DEBUG: Is image edit request: {is_image_edit_request}")
            print(f"🎨 DEBUG: Is color edit request: {is_color_edit_request}")
            print(f"🎯 DEBUG: Base image for edit: {base_image_url if base_image_url else 'None'}")
            print(f"🎯 DEBUG: Final prompt for image generation: '{enhanced_prompt}'")
            
            print(f"🔧 DEBUG: About to process style image...")
            
            # טיפול בתמונת סטייל שהועלתה על ידי המשתמש
            style_reference_url = None
            if style_image:
                print(f"🎨 DEBUG: Processing style image: {style_image}")
                try:
                    print("🎨 Processing style reference image")
                    
                    # יצירת שם קובץ ייחודי לתמונת הסטייל
                    unique_id = str(uuid.uuid4().hex[:16])
                    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                    
                    # קביעת סיומת הקובץ
                    file_extension = 'png'  # Default
                    if hasattr(style_image, 'name') and style_image.name:
                        original_extension = style_image.name.lower().split('.')[-1]
                        if original_extension in ['jpg', 'jpeg', 'png', 'webp']:
                            file_extension = original_extension if original_extension != 'jpeg' else 'jpg'
                    
                    filename = f"style_ref_{unique_id}_{timestamp}.{file_extension}"
                    
                    # שמירת התמונה בתיקיית מדיה
                    style_dir = os.path.join(settings.MEDIA_ROOT, 'style_references')
                    os.makedirs(style_dir, exist_ok=True)
                    
                    file_path = os.path.join(style_dir, filename)
                    
                    # פתיחת התמונה ועיבוד
                    with Image.open(style_image) as img:
                        # המרה ל-RGB אם יש צורך
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')
                        
                        # שמירה באיכות גבוהה
                        img.save(file_path, format='JPEG' if file_extension == 'jpg' else file_extension.upper(), 
                                quality=95, dpi=(300, 300))
                    
                    # יצירת URL לתמונה
                    style_reference_url = request.build_absolute_uri(f"/media/style_references/{filename}")
                    
                    print(f"✅ Style reference image saved: {style_reference_url}")
                    
                except Exception as e:
                    print(f"❌ Error processing style image: {str(e)}")
                    # ממשיכים גם אם יש שגיאה בעיבוד תמונת הסטייל
            else:
                print(f"🎨 DEBUG: No style image provided")
                    
            print(f"🚀 DEBUG: About to start AI generation...")
            
            # Generate image using AI - Choose between Flux Pro 1.1 or Freepik AI
            try:
                # Check which AI service to use
                replicate_api_key = getattr(settings, 'REPLICATE_API_KEY', None)
                freepik_api_key = getattr(settings, 'FREEPIK_API_KEY', None)
                
                print("=" * 80)
                print("🔍 AI ENGINE SELECTION DEBUG:")
                print(f"🔑 Replicate API Key: {'✅ FOUND' if replicate_api_key else '❌ NOT FOUND'}")
                if replicate_api_key:
                    print(f"🔑 Replicate Key Length: {len(replicate_api_key)} characters")
                    print(f"🔑 Replicate Key Preview: {replicate_api_key[:8]}...")
                    
                print(f"🔑 Freepik API Key: {'✅ FOUND' if freepik_api_key else '❌ NOT FOUND'}")
                if freepik_api_key:
                    print(f"🔑 Freepik Key Length: {len(freepik_api_key)} characters")
                    print(f"🔑 Freepik Key Preview: {freepik_api_key[:8]}...")
                print("=" * 80)
                
                # Prefer Flux Pro 1.1 if available, otherwise use Freepik
                if replicate_api_key:
                    print("🚀🚀🚀 SELECTED ENGINE: FLUX PRO 1.1 VIA REPLICATE 🚀🚀🚀")
                    
                    # Use clean prompt for Flux
                    clean_prompt = clean_prompt_for_ai(enhanced_prompt, is_color_edit=is_color_edit_request)
                    
                    # בדיקה אם להשתמש ב-Image-to-Image או Text-to-Image
                    if is_image_edit_request and base_image_url:
                        print("🔄 Using Image-to-Image mode with user-selected image")
                        print(f"📷 Base image URL: {base_image_url}")
                        
                        # Send to Flux Pro 1.1 with image input (Image-to-Image)
                        # Use higher strength for color changes and modifications
                        if is_color_edit_request:
                            print("🎨 Using ENHANCED COLOR EDIT mode")
                            strength_value = 0.95  # Very very high strength for dramatic color changes
                        else:
                            strength_value = 0.8  # High strength for general edits
                            
                        image_url = send_flux_request(clean_prompt, replicate_api_key, 
                                                    init_image=base_image_url, strength=strength_value, 
                                                    style_image=style_reference_url, is_color_edit=is_color_edit_request)
                    else:
                        print("✨ Using Text-to-Image mode")
                        if style_reference_url:
                            print("🎨 Including style reference")
                        # Send to Flux Pro 1.1 (Text-to-Image)
                        image_url = send_flux_request(clean_prompt, replicate_api_key, 
                                                    style_image=style_reference_url, is_color_edit=False)
                    
                    # Download the image from Flux
                    img_response = requests.get(image_url, timeout=30)
                    if img_response.status_code == 200:
                        image_bytes = img_response.content
                        ai_service_name = "Flux Pro 1.1"
                    else:
                        raise Exception(f'Failed to download image from Flux URL: {img_response.status_code}')
                        
                elif freepik_api_key:
                    print("🎨🎨🎨 SELECTED ENGINE: FREEPIK AI (FALLBACK) 🎨🎨🎨")
                    print("⚠️ WARNING: Using Freepik instead of Flux Pro 1.1!")
                    
                    # Use Freepik AI as fallback
                    headers = {
                        'X-Freepik-API-Key': freepik_api_key,
                        'Content-Type': 'application/json'
                    }
                    
                    final_prompt = enhanced_prompt
                    clean_prompt = clean_prompt_for_ai(final_prompt, is_color_edit=is_color_edit_request)
                    
                    # בחירת API endpoint ו-payload לפי סוג הבקשה
                    if is_image_edit_request and base_image_url:
                        print("🔄 Using Freepik Image-to-Image mode with user-selected image")
                        print(f"📷 Base image URL: {base_image_url}")
                        
                        # שימוש ב-Image-to-Image API של Freepik
                        api_url = 'https://api.freepik.com/v1/ai/image-to-image'
                        payload = {
                            'prompt': clean_prompt,
                            'image': base_image_url,
                            'strength': 0.7,  # רמת השינוי (0.1=שינוי קל, 1.0=שינוי מלא)
                            'num_inference_steps': 50,
                            'guidance_scale': 7.5,
                            'num_images': 1
                        }
                    else:
                        print("✨ Using Freepik Text-to-Image mode")
                        if style_reference_url:
                            print("🎨 Including style reference for Freepik")
                        # שימוש ב-Text-to-Image API רגיל של Freepik
                        api_url = 'https://api.freepik.com/v1/ai/text-to-image'
                        payload = create_freepik_payload(clean_prompt, style_reference_url)
                    
                    print("=" * 60)
                    print("📤 FREEPIK API REQUEST:")
                    print(f"URL: {api_url}")
                    print(f"Payload: {payload}")
                    print("=" * 60)
                    
                    response = requests.post(
                        api_url,
                        headers=headers,
                        json=payload,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'data' in result and len(result['data']) > 0:
                            first_item = result['data'][0]
                            if 'base64' in first_item:
                                image_bytes = base64.b64decode(first_item['base64'])
                                ai_service_name = "Freepik AI"
                            else:
                                raise Exception("No base64 data in Freepik response")
                        else:
                            raise Exception("No images in Freepik AI response")
                    else:
                        error_response = response.json() if response.text else {}
                        error_msg = error_response.get('message', 'Unknown Freepik AI error')
                        raise Exception(f'Freepik AI service error: {error_msg}')
                else:
                    print("❌❌❌ NO AI ENGINE AVAILABLE! ❌❌❌")
                    print("💥 ERROR: Neither Replicate nor Freepik API keys were found!")
                    return JsonResponse({
                        'success': False, 
                        'error': 'No AI service configured. Please add REPLICATE_API_KEY (preferred) or FREEPIK_API_KEY to your settings.'
                    })
                # Process the image (common for both services)
                print("=" * 60)
                print("🖼️ IMAGE PROCESSING:")
                print(f"Raw image size: {len(image_bytes)} bytes")
                print(f"AI Service: {ai_service_name}")
                print("Starting PIL image processing...")
                print("=" * 60)
                
                try:
                    # Open the image with PIL
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Convert to RGBA to ensure transparency support
                    if image.mode != 'RGBA':
                        image = image.convert('RGBA')
                    
                    # Remove white background and make it transparent
                    image = remove_white_background(image)
                    
                    # Calculate target size based on product dimensions
                    target_size = (int(max_width), int(max_height))
                    
                    # Resize with high quality resampling for smooth curves
                    # Use LANCZOS for the best quality when resizing
                    image = image.resize(target_size, Image.Resampling.LANCZOS)
                    
                    # Apply additional smoothing filter for better edges
                    from PIL import ImageFilter
                    # Apply a slight smoothing filter to reduce pixelation
                    image = image.filter(ImageFilter.SMOOTH_MORE)
                    
                    # Set DPI to 300 for print quality
                    image.info['dpi'] = (300, 300)
                    
                    # Save the processed image to a BytesIO buffer with 300 DPI
                    output_buffer = io.BytesIO()
                    image.save(output_buffer, format='PNG', optimize=True, quality=100, dpi=(300, 300))
                    output_buffer.seek(0)
                    
                    # Also create a CMYK version for printing
                    cmyk_buffer = io.BytesIO()
                    # Convert RGBA to RGB first (remove alpha channel with white background for CMYK)
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                    
                    # Convert RGB to CMYK
                    cmyk_image = rgb_image.convert('CMYK')
                    cmyk_image.save(cmyk_buffer, format='TIFF', dpi=(300, 300), compression='lzw')
                    cmyk_buffer.seek(0)
                    
                    # Create unique filenames
                    base_filename = f"ai_design_{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    png_filename = f"{base_filename}.png"
                    cmyk_filename = f"{base_filename}_cmyk.tif"
                    
                    print("=" * 60)
                    print("💾 SAVING FILES:")
                    print(f"PNG filename: {png_filename}")
                    print(f"CMYK filename: {cmyk_filename}")
                    print("=" * 60)
                    
                    # Save PNG version to media directory
                    png_file_path = os.path.join('ai_designs', png_filename)
                    png_saved_path = default_storage.save(png_file_path, ContentFile(output_buffer.getvalue()))
                    
                    # Save CMYK version to media directory
                    cmyk_file_path = os.path.join('ai_designs', cmyk_filename)
                    cmyk_saved_path = default_storage.save(cmyk_file_path, ContentFile(cmyk_buffer.getvalue()))
                    
                    # Get full URLs
                    png_url = request.build_absolute_uri(default_storage.url(png_saved_path))
                    cmyk_url = request.build_absolute_uri(default_storage.url(cmyk_saved_path))
                    
                    print("=" * 60)
                    print("🎉 FINAL RESULT:")
                    print(f"PNG URL: {png_url}")
                    print(f"CMYK URL: {cmyk_url}")
                    print(f"AI Service Used: {ai_service_name}")
                    print("=" * 60)
                    
                    # Save AI response to conversation
                    ai_message = AIMessage.objects.create(
                        conversation=conversation,
                        message_type='ai',
                        content=f"Generated image: {png_filename}",
                        translated_prompt=enhanced_prompt,
                        generated_image_url=png_url,
                        ai_service_used=ai_service_name,
                        metadata={
                            'cmyk_url': cmyk_url,
                            'dimensions': f'{target_size[0]}x{target_size[1]} pixels',
                            'dpi': '300 DPI',
                            'max_print_size': f'{max_width/118.11:.1f}x{max_height/118.11:.1f} cm',
                            'used_image_to_image': is_image_edit_request and bool(base_image_url),
                            'base_image_url': base_image_url if (is_image_edit_request and base_image_url) else None,
                            'user_selected_edit': is_image_edit_request
                        }
                    )
                    
                    response_data = {
                        'success': True,
                        'image_url': png_url,
                        'cmyk_url': cmyk_url,
                        'filename': png_filename,
                        'cmyk_filename': cmyk_filename,
                        'dimensions': f'{target_size[0]}x{target_size[1]} pixels',
                        'dpi': '300 DPI',
                        'max_print_size': f'{max_width/118.11:.1f}x{max_height/118.11:.1f} cm',
                        'ai_service': ai_service_name,
                        'conversation_id': conversation.id,  # שליחת מזהה השיחה
                        'conversation_title': conversation.title,
                        'used_image_to_image': is_image_edit_request and bool(base_image_url),
                        'base_image_url': base_image_url if (is_image_edit_request and base_image_url) else None
                    }
                    
                    return JsonResponse(response_data)
                    
                except Exception as img_error:
                    return JsonResponse({
                        'success': False,
                        'error': f'Image processing error: {str(img_error)}'
                    })
                    
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'AI service error: {str(e)}'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@csrf_exempt 
def get_ai_conversations(request):
    """קבלת רשימת שיחות AI של המשתמש"""
    if request.method == 'GET':
        try:
            session_id = get_or_create_session_id(request)
            
            if request.user.is_authenticated:
                # רשימת שיחות עבור משתמש מחובר (לפי user + session)
                conversations = AIConversation.objects.filter(
                    models.Q(user=request.user) | models.Q(session_id=session_id, user__isnull=True)
                )
            else:
                # רשימת שיחות עבור משתמש אנונימי לפי session בלבד
                conversations = AIConversation.objects.filter(session_id=session_id, user__isnull=True)
            
            conversations_data = []
            for conv in conversations.order_by('-updated_at')[:20]:  # 20 שיחות אחרונות
                last_message = conv.messages.order_by('-created_at').first()
                conversations_data.append({
                    'id': conv.id,
                    'title': conv.title,
                    'product_name': conv.product.name if conv.product else None,
                    'created_at': conv.created_at.isoformat(),
                    'updated_at': conv.updated_at.isoformat(),
                    'message_count': conv.messages.count(),
                    'last_message': last_message.content[:100] if last_message else None,
                })
            
            return JsonResponse({
                'success': True,
                'conversations': conversations_data
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@csrf_exempt
def get_conversation_history(request):
    """קבלת היסטוריית שיחה ספציפית"""
    if request.method == 'GET':
        try:
            conversation_id = request.GET.get('conversation_id')
            if not conversation_id:
                return JsonResponse({'success': False, 'error': 'חסר מזהה שיחה'})
            
            session_id = get_or_create_session_id(request)
            
            # Get conversation
            if request.user.is_authenticated:
                # חיפוש לפי user או session
                conversation = AIConversation.objects.get(
                    models.Q(id=conversation_id) & 
                    (models.Q(user=request.user) | models.Q(session_id=session_id, user__isnull=True))
                )
            else:
                # משתמש אנונימי - חיפוש לפי session בלבד
                conversation = AIConversation.objects.get(
                    id=conversation_id, 
                    session_id=session_id,
                    user__isnull=True
                )
            
            # Get messages
            messages = []
            for message in conversation.messages.order_by('created_at'):
                message_data = {
                    'id': message.id,
                    'type': message.message_type,
                    'content': message.content,
                    'created_at': message.created_at.isoformat(),
                }
                
                # Add AI-specific data
                if message.message_type == 'ai':
                    message_data.update({
                        'translated_prompt': message.translated_prompt,
                        'image_url': message.generated_image_url,
                        'ai_service': message.ai_service_used,
                        'metadata': message.metadata,
                    })
                
                messages.append(message_data)
            
            return JsonResponse({
                'success': True,
                'conversation': {
                    'id': conversation.id,
                    'title': conversation.title,
                    'product_name': conversation.product.name if conversation.product else None,
                    'created_at': conversation.created_at.isoformat(),
                    'updated_at': conversation.updated_at.isoformat(),
                },
                'messages': messages
            })
            
        except AIConversation.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'שיחה לא נמצאה'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


def remove_white_background(image):
    """Remove white and light gray background from image and make it transparent while preserving smooth edges"""
    # Convert to RGBA if not already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Get image data
    data = image.getdata()
    
    # Create new image data with transparency
    new_data = []
    for item in data:
        r, g, b = item[0], item[1], item[2]
        
        # Calculate brightness and color variance
        brightness = (r + g + b) / 3
        color_variance = max(r, g, b) - min(r, g, b)
        
        # If pixel is very close to white (brightness > 245 and low variance)
        if brightness > 245 and color_variance < 15:
            # Make it completely transparent
            new_data.append((255, 255, 255, 0))
        # If pixel is light gray/white (brightness > 230 and low variance)
        elif brightness > 230 and color_variance < 25:
            # Make it mostly transparent
            new_data.append((255, 255, 255, 0))
        # If pixel is medium gray (brightness > 200 and low variance)
        elif brightness > 200 and color_variance < 30:
            # Make it partially transparent based on how gray it is
            alpha = max(0, int((200 - brightness) * 8))
            new_data.append((r, g, b, alpha))
        # If pixel is light but has some color (anti-aliasing pixels)
        elif brightness > 180 and color_variance < 40:
            # Make it partially transparent to preserve smooth edges
            alpha = max(0, int((180 - brightness) * 6))
            new_data.append((r, g, b, alpha))
        else:
            # Keep original pixel with full opacity
            new_data.append(item)
    
    # Update image data
    image.putdata(new_data)
    return image

def ai_conversation_demo(request):
    """דף דמו לשיחות AI"""
    # קרא את הקובץ HTML ישירות
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_conversation_demo.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return HttpResponse(html_content, content_type='text/html')

@csrf_exempt
def search_freepik_images(request):
    """חיפוש תמונות במאגר של Freepik - עם fallback ל-Unsplash/Pixabay"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        search_query = data.get('query', '').strip()
        
        if not search_query:
            return JsonResponse({'error': 'Search query is required'}, status=400)
        
        # Try Freepik first, then fallback to free APIs
        freepik_api_key = getattr(settings, 'FREEPIK_API_KEY', None)
        
        print(f"🔍 Searching for images: '{search_query}'")
        print(f"🔑 Freepik API Key Status: {'✅ Available' if freepik_api_key and freepik_api_key.strip() else '❌ Not configured'}")
        
        # First, try Freepik if we have an API key
        if freepik_api_key and freepik_api_key.strip():
            print("🚀 Trying Freepik API first...")
            try:
                result = search_freepik_api(search_query, freepik_api_key)
                if result:
                    return result
            except Exception as e:
                print(f"⚠️ Freepik API failed: {str(e)}")
        else:
            print("⚠️ Freepik API key not configured - using fallback APIs")
        
        # Fallback to Unsplash (free API)
        print("🚀 Trying Unsplash API as fallback...")
        try:
            result = search_unsplash_api(search_query)
            if result:
                return result
        except Exception as e:
            print(f"⚠️ Unsplash API failed: {str(e)}")
        
        # Final fallback to Pixabay (free API)
        try:
            result = search_pixabay_api(search_query)
            if result:
                return result
        except Exception as e:
            print(f"⚠️ Pixabay API failed: {str(e)}")
        
        # If all APIs fail, return error
        return JsonResponse({
            'error': 'כל שירותי החיפוש אינם זמינים כרגע. נסה שוב מאוחר יותר.'
        }, status=503)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        print(f"❌ Unexpected error in search_freepik_images: {str(e)}")
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

def analyze_image_transparency_potential(title, tags, image_url, source_type):
    """מחזירה ניקוד מ-0 עד 100 לסבירות שהתמונה מתאימה לרקע שקוף"""
    score = 0
    title_lower = title.lower() if title else ''
    tags_text = ' '.join(tags).lower() if tags else ''
    url_lower = image_url.lower() if image_url else ''
    combined_text = f"{title_lower} {tags_text}".strip()
    
    # מילות מפתח חזקות שמעידות על רקע שקוף
    strong_transparent_keywords = [
        'transparent', 'png', 'cutout', 'isolated', 'logo', 'icon', 'vector',
        'no background', 'white background', 'cut out', 'clip art', 'clipart',
        'symbol', 'badge', 'sticker', 'graphic element'
    ]
    
    # מילות מפתח בעברית
    hebrew_keywords = [
        'לוגו', 'איקון', 'סמל', 'מדבקה', 'איור', 'גרפיקה', 'וקטור'
    ]
    
    # מילות מפתח בינוניות
    medium_keywords = [
        'illustration', 'design', 'minimal', 'simple', 'flat', 'graphic',
        'silhouette', 'outline', 'drawing', 'art'
    ]
    
    # בדיקת מילות מפתח חזקות
    for keyword in strong_transparent_keywords:
        if keyword in combined_text:
            score += 30
    
    # בדיקת מילות מפתח בעברית
    for keyword in hebrew_keywords:
        if keyword in combined_text:
            score += 25
    
    # בדיקת מילות מפתח בינוניות
    for keyword in medium_keywords:
        if keyword in combined_text:
            score += 15
    
    # בדיקת סוג קובץ בURL
    if '.png' in url_lower:
        score += 20
    elif '.svg' in url_lower:
        score += 25
    
    # בונוס למקור Freepik עם תגיות רלוונטיות
    if source_type == 'freepik':
        if any(word in combined_text for word in ['vector', 'illustration', 'graphic']):
            score += 10
    
    return min(score, 100)  # מקסימום 100

def analyze_vector_potential(title, tags, image_url):
    """מחזירה ניקוד מ-0 עד 100 לסבירות שהתמונה היא וקטורית"""
    score = 0
    title_lower = title.lower() if title else ''
    tags_text = ' '.join(tags).lower() if tags else ''
    url_lower = image_url.lower() if image_url else ''
    combined_text = f"{title_lower} {tags_text}".strip()
    
    vector_keywords = [
        'vector', 'svg', 'illustration', 'graphic', 'logo', 'icon',
        'flat design', 'minimal', 'simple', 'geometric', 'abstract',
        'symbol', 'badge', 'clean', 'modern'
    ]
    
    hebrew_vector_keywords = [
        'וקטור', 'איור', 'לוגו', 'איקון', 'סמל', 'עיצוב', 'גרפיקה'
    ]
    
    # בדיקת מילות מפתח
    for keyword in vector_keywords:
        if keyword in combined_text:
            score += 20
    
    for keyword in hebrew_vector_keywords:
        if keyword in combined_text:
            score += 20
    
    # בדיקת סוג קובץ
    if '.svg' in url_lower:
        score += 40
    elif '.png' in url_lower:
        score += 10  # PNG יכול להיות וקטורי
    
    return min(score, 100)

def search_freepik_api(search_query, api_key):
    """חיפוש תמונות ב-Freepik - עם ה-API הנכון ושיפור לתמונות שקופות"""
    headers = {
        'x-freepik-api-key': api_key,  # Correct header name
        'Accept-Language': 'en-US',
    }
    
    # Enhanced search logic for transparent images
    enhanced_query = search_query
    
    # If user is looking for transparent images, enhance the search
    transparency_keywords = ['שקוף', 'רקע שקוף', 'ללא רקע', 'transparent', 'no background', 'cutout']
    vector_keywords = ['וקטור', 'לוגו', 'איקון', 'vector', 'logo', 'icon']
    
    is_transparency_search = any(keyword in search_query.lower() for keyword in transparency_keywords)
    is_vector_search = any(keyword in search_query.lower() for keyword in vector_keywords)
    
    if is_transparency_search or is_vector_search:
        # Add search terms that improve results for transparent images
        enhanced_query += " transparent background vector logo icon isolated cutout"
    
    # Parameters according to official documentation
    search_params = {
        'term': enhanced_query,
        'limit': 20,
        'page': 1,
        'order': 'relevance',
        'filters[content_type][photo]': 1,  # Only photos
        'filters[license][freemium]': 1,    # Free resources
    }
    
    # Add vector filter if searching for vector content
    if is_vector_search:
        search_params['filters[content_type][vector]'] = 1
        search_params.pop('filters[content_type][photo]', None)  # Remove photo filter
    
    api_url = 'https://api.freepik.com/v1/resources'
    
    print(f"🌐 Freepik API Request:")
    print(f"   URL: {api_url}")
    print(f"   Enhanced Query: {enhanced_query}")
    print(f"   Params: {search_params}")
    print(f"   API Key: {api_key[:8]}..." if api_key else "   API Key: None")
    
    response = requests.get(api_url, headers=headers, params=search_params, timeout=30)
    
    print(f"🌐 Freepik API Response Status: {response.status_code}")
    
    if response.status_code == 200:
        search_results = response.json()
        print(f"🌐 Raw response keys: {search_results.keys() if search_results else 'None'}")
        
        processed_results = []
        
        if 'data' in search_results:
            for item in search_results['data']:
                # Extract image information according to API response structure
                image_data = item.get('image', {})
                source_data = image_data.get('source', {})
                title = item.get('title', 'Untitled')
                tags = item.get('related', {}).get('keywords', [])
                thumbnail_url = source_data.get('url', '')
                
                # Analyze transparency and vector potential
                transparency_score = analyze_image_transparency_potential(
                    title, tags, thumbnail_url, 'freepik'
                )
                vector_score = analyze_vector_potential(title, tags, thumbnail_url)
                
                processed_item = {
                    'id': str(item.get('id', '')),
                    'title': title,
                    'thumbnail': thumbnail_url,
                    'preview': thumbnail_url,  # Same URL for now
                    'tags': tags,
                    'type': 'freepik',
                    'source': 'Freepik',
                    'url': item.get('url', ''),  # Original Freepik page
                    'author': item.get('author', {}).get('name', 'Unknown'),
                    'downloads': item.get('stats', {}).get('downloads', 0),
                    'orientation': image_data.get('orientation', 'unknown'),
                    'transparency_score': transparency_score,
                    'vector_score': vector_score,
                    'is_likely_transparent': transparency_score >= 50,
                    'is_likely_vector': vector_score >= 60
                }
                
                # Only add items with valid image URLs
                if processed_item['thumbnail']:
                    processed_results.append(processed_item)
        
        print(f"✅ Found {len(processed_results)} images from Freepik")
        
        if processed_results:
            return JsonResponse({
                'success': True,
                'results': processed_results,
                'total': len(processed_results),
                'source': 'Freepik'
            })
    
    elif response.status_code == 401:
        print(f"❌ Freepik API authentication failed: Invalid API key")
        return None
    elif response.status_code == 403:
        print(f"❌ Freepik API forbidden: Check your subscription/credits")
        return None
    else:
        try:
            error_data = response.json()
            print(f"❌ Freepik API error response: {error_data}")
        except:
            print(f"❌ Freepik API error: {response.status_code} - {response.text[:200]}")
    
    return None

def search_unsplash_api(search_query):
    """חיפוש תמונות ב-Unsplash (חינם)"""
    # Using Unsplash's source API (no key required)
    try:
        # Translate Hebrew to English for better results
        if any('\u0590' <= char <= '\u05ff' for char in search_query):
            # Simple translation mapping for common Hebrew terms
            translations = {
                'בננה': 'banana',
                'כלב': 'dog',
                'חתול': 'cat',
                'פרח': 'flower',
                'עץ': 'tree',
                'בית': 'house',
                'רכב': 'car',
                'אוכל': 'food',
                'טבע': 'nature',
                'ים': 'sea'
            }
            search_query = translations.get(search_query, search_query)
        
        processed_results = []
        
        # Create sample results from Unsplash
        for i in range(12):
            item_id = f"unsplash_{i}_{search_query}"
            title = f'{search_query.title()} Image {i+1}'
            thumbnail_url = f'https://source.unsplash.com/200x200/?{search_query}&sig={i}'
            
            # Analyze transparency and vector potential
            transparency_score = analyze_image_transparency_potential(
                title, [search_query], thumbnail_url, 'unsplash'
            )
            vector_score = analyze_vector_potential(title, [search_query], thumbnail_url)
            
            processed_item = {
                'id': item_id,
                'title': title,
                'thumbnail': thumbnail_url,
                'preview': f'https://source.unsplash.com/400x400/?{search_query}&sig={i}',
                'tags': [search_query],
                'type': 'unsplash',
                'source': 'Unsplash',
                'transparency_score': transparency_score,
                'vector_score': vector_score,
                'is_likely_transparent': transparency_score >= 50,
                'is_likely_vector': vector_score >= 60
            }
            processed_results.append(processed_item)
        
        print(f"✅ Generated {len(processed_results)} images from Unsplash")
        return JsonResponse({
            'success': True,
            'results': processed_results,
            'total': len(processed_results),
            'source': 'Unsplash (Free)'
        })
    
    except Exception as e:
        print(f"❌ Unsplash error: {str(e)}")
        return None

def search_pixabay_api(search_query):
    """חיפוש תמונות ב-Pixabay (fallback נוסף)"""
    try:
        # Translate Hebrew to English for better results
        if any('\u0590' <= char <= '\u05ff' for char in search_query):
            translations = {
                'בננה': 'banana',
                'כלב': 'dog',
                'חתול': 'cat',
                'פרח': 'flower',
                'עץ': 'tree',
                'בית': 'house',
                'רכב': 'car',
                'אוכל': 'food',
                'טבע': 'nature',
                'ים': 'sea'
            }
            search_query = translations.get(search_query, search_query)
        
        processed_results = []
        
        # Create sample results
        for i in range(8):
            item_id = f"pixabay_{i}_{search_query}"
            title = f'{search_query.title()} Stock {i+1}'
            thumbnail_url = f'https://via.placeholder.com/150x150/4a90e2/ffffff?text={search_query[:3].upper()}{i+1}'
            
            # Analyze transparency and vector potential
            transparency_score = analyze_image_transparency_potential(
                title, [search_query, 'stock'], thumbnail_url, 'pixabay'
            )
            vector_score = analyze_vector_potential(title, [search_query, 'stock'], thumbnail_url)
            
            processed_item = {
                'id': item_id,
                'title': title,
                'thumbnail': thumbnail_url,
                'preview': f'https://via.placeholder.com/300x300/4a90e2/ffffff?text={search_query[:3].upper()}{i+1}',
                'tags': [search_query, 'stock'],
                'type': 'pixabay',
                'source': 'Stock Images',
                'transparency_score': transparency_score,
                'vector_score': vector_score,
                'is_likely_transparent': transparency_score >= 50,
                'is_likely_vector': vector_score >= 60
            }
            processed_results.append(processed_item)
        
        print(f"✅ Generated {len(processed_results)} placeholder images")
        return JsonResponse({
            'success': True,
            'results': processed_results,
            'total': len(processed_results),
            'source': 'Stock Images'
        })
    
    except Exception as e:
        print(f"❌ Pixabay error: {str(e)}")
        return None

@csrf_exempt
def download_freepik_image(request):
    """הורדת תמונה והוספה לעיצוב"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        image_id = data.get('image_id')
        image_url = data.get('image_url')
        image_title = data.get('image_title', 'Image')
        
        if not image_id or not image_url:
            return JsonResponse({'error': 'Image ID and URL are required'}, status=400)
        
        print(f"📥 Downloading image: {image_id}")
        
        # Add headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # הורדת התמונה
        response = requests.get(image_url, headers=headers, timeout=30)
        if response.status_code == 200:
            # יצירת שם קובץ ייחודי
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            image_type = image_id.split('_')[0] if '_' in image_id else 'stock'
            filename = f"{image_type}_{image_id.replace('/', '_')}_{timestamp}.jpg"
            
            # שמירת התמונה בתיקיית media
            media_path = os.path.join(settings.MEDIA_ROOT, 'freepik_images')
            os.makedirs(media_path, exist_ok=True)
            
            file_path = os.path.join(media_path, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # URL יחסי לתמונה
            image_url = os.path.join(settings.MEDIA_URL, 'freepik_images', filename).replace('\\', '/')
            
            print(f"✅ Image saved: {filename}")
            return JsonResponse({
                'success': True,
                'image_url': image_url,
                'filename': filename,
                'title': image_title
            })
        else:
            print(f"❌ Failed to download image: HTTP {response.status_code}")
            return JsonResponse({'error': f'Failed to download image: {response.status_code}'}, status=500)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Download timeout - try again'}, status=408)
    except requests.exceptions.RequestException as e:
        print(f"❌ Download error: {str(e)}")
        return JsonResponse({'error': f'Download error: {str(e)}'}, status=500)
    except Exception as e:
        print(f"❌ Unexpected error in download_freepik_image: {str(e)}")
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)


@csrf_exempt
def remove_background(request):
    """הסרת רקע מתמונה באמצעות rembg"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        # Parse JSON data
        data = json.loads(request.body)
        image_url = data.get('image_url', '').strip()
        
        if not image_url:
            return JsonResponse({'error': 'No image URL provided'}, status=400)
        
        print(f"🔍 Processing background removal for: {image_url}")
        
        # Import required libraries
        try:
            from rembg import remove
            import numpy as np
            from PIL import Image, ImageFilter
            import cv2
        except ImportError:
            return JsonResponse({
                'error': 'Background removal library not installed. Please install rembg: pip install rembg'
            }, status=500)
        
        # Download image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Handle both local and remote URLs
        if image_url.startswith(('http://', 'https://')):
            response = requests.get(image_url, headers=headers, timeout=30)
            if response.status_code != 200:
                return JsonResponse({'error': f'Failed to download image: {response.status_code}'}, status=500)
            image_data = response.content
        else:
            # Local file
            if image_url.startswith('/media/'):
                image_path = os.path.join(settings.MEDIA_ROOT, image_url.replace('/media/', ''))
            else:
                image_path = os.path.join(settings.MEDIA_ROOT, image_url)
            
            if not os.path.exists(image_path):
                return JsonResponse({'error': 'Image file not found'}, status=404)
            
            with open(image_path, 'rb') as f:
                image_data = f.read()
        
        # Process image with rembg
        print("🎨 Removing background...")
        output_image = remove(image_data)
        
        # Convert to PIL Image for further processing
        from io import BytesIO
        img = Image.open(BytesIO(output_image))
        
        # Apply expand effect (similar to Photoshop's Modify > Expand)
        print("🔧 Applying expand effect...")
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Get alpha channel (transparency mask)
        alpha = img.split()[-1]
        
        # Apply morphological closing to expand the mask (removes small holes)
        alpha_array = np.array(alpha)
        
        # Create kernel for morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        
        # Apply closing operation (dilation followed by erosion)
        # This fills small gaps and expands the mask slightly
        closed_mask = cv2.morphologyEx(alpha_array, cv2.MORPH_CLOSE, kernel)
        
        # Apply slight erosion to clean background pixels
        eroded_mask = cv2.erode(closed_mask, kernel, iterations=1)
        
        # Convert back to PIL Image
        cleaned_alpha = Image.fromarray(eroded_mask, mode='L')
        
        # Apply slight blur to smooth edges
        cleaned_alpha = cleaned_alpha.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Combine RGB channels with the cleaned alpha
        rgb_channels = img.split()[:3]
        final_img = Image.merge('RGBA', rgb_channels + (cleaned_alpha,))
        
        # Save processed image
        print("💾 Saving processed image...")
        output_buffer = BytesIO()
        final_img.save(output_buffer, format='PNG', optimize=True)
        final_output = output_buffer.getvalue()
        
        # Save processed image
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"no_bg_{timestamp}.png"
        
        media_path = os.path.join(settings.MEDIA_ROOT, 'processed_images')
        os.makedirs(media_path, exist_ok=True)
        
        file_path = os.path.join(media_path, filename)
        with open(file_path, 'wb') as f:
            f.write(final_output)
        
        # Create URL for the processed image
        processed_image_url = os.path.join(settings.MEDIA_URL, 'processed_images', filename).replace('\\', '/')
        
        print(f"✅ Background removed and cleaned successfully: {filename}")
        
        return JsonResponse({
            'success': True,
            'processed_image_url': processed_image_url,
            'original_url': image_url,
            'filename': filename,
            'processing_steps': ['background_removal', 'expand', 'smooth_edges']
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Image download timeout'}, status=408)
    except Exception as e:
        print(f"❌ Error in remove_background: {str(e)}")
        return JsonResponse({'error': f'Background removal failed: {str(e)}'}, status=500)
