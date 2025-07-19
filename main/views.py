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
import json
import requests
import base64
import os
import uuid
from datetime import datetime
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image
import io
from datetime import datetime
import uuid
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
    """יצירת עיצוב באמצעות AI עם תמיכה בהיסטוריית שיחה"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '')
            product_id = data.get('product_id', '')
            product_name = data.get('product_name', '')
            conversation_id = data.get('conversation_id', None)  # מזהה שיחה קיימת
            
            print(f"📥 DEBUG: POST request received")
            print(f"📥 DEBUG: prompt: '{prompt}'")
            print(f"📥 DEBUG: product_id: {product_id}")
            print(f"📥 DEBUG: conversation_id: {conversation_id}")
            
            if not prompt:
                return JsonResponse({'success': False, 'error': 'חסר תיאור עיצוב'})
            
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
                    product_id=product_id if product_id else None,
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
            
            # Get product dimensions if product_id is provided
            max_width = 396.8  # Default width in pixels
            max_height = 453.5  # Default height in pixels
            
            if product_id:
                try:
                    product = Product.objects.get(id=product_id, is_active=True)
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
                except Product.DoesNotExist:
                    pass
            
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
            
            # בדיקה אם יש תמונה קודמת לשימוש כבסיס לשינוי
            last_image_url = None
            modification_keywords = [
                "שנה", "שני", "אדום", "כחול", "ירוק", "צהוב", "סגול", "כתום", "ורוד", "שחור", "לבן",
                "זווית", "מזווית", "צד", "מימין", "משמאל", "מלמעלה", "מלמטה", 
                "גדול יותר", "קטן יותר", "עבה יותר", "דק יותר",
                "עם", "בלי", "הוסף", "הסר", "החלף"
            ]
            
            # חיפוש התמונה האחרונה מההיסטוריה
            print(f"🔍 DEBUG: Searching for previous images in conversation {conversation.id}")
            print(f"🔍 DEBUG: Total messages in conversation: {conversation.messages.count()}")
            
            all_ai_messages = conversation.messages.filter(message_type='ai')
            print(f"🔍 DEBUG: AI messages found: {all_ai_messages.count()}")
            
            ai_messages_with_images = all_ai_messages.filter(generated_image_url__isnull=False)
            print(f"🔍 DEBUG: AI messages with images: {ai_messages_with_images.count()}")
            
            last_ai_message = ai_messages_with_images.order_by('-created_at').first()
            
            if last_ai_message:
                last_image_url = last_ai_message.generated_image_url
                print(f"🔍 DEBUG: Found last image: {last_image_url}")
            else:
                print("🔍 DEBUG: No previous images found in this conversation")
            
            # בדיקה אם הבקשה היא לשינוי תמונה קיימת
            is_modification_request = any(keyword in simple_prompt.lower() for keyword in modification_keywords)
            
            print(f"🎯 DEBUG: Is modification request: {is_modification_request}")
            print(f"🎯 DEBUG: Has previous image: {bool(last_image_url)}")
            print(f"🎯 DEBUG: Final prompt for image generation: '{enhanced_prompt}'")
            
            # Generate image using AI - Choose between Flux Pro 1.1 or Freepik AI
            try:
                # Check which AI service to use
                replicate_api_key = getattr(settings, 'REPLICATE_API_KEY', None)
                freepik_api_key = getattr(settings, 'FREEPIK_API_KEY', None)
                
                print(f"Replicate API Key: {'Found' if replicate_api_key else 'Not found'}")
                print(f"Freepik API Key: {'Found' if freepik_api_key else 'Not found'}")
                
                # Prefer Flux Pro 1.1 if available, otherwise use Freepik
                if replicate_api_key:
                    print("🚀 Using Flux Pro 1.1 via Replicate")
                    
                    # Use clean prompt for Flux
                    clean_prompt = clean_prompt_for_ai(enhanced_prompt)
                    
                    # בדיקה אם להשתמש ב-Image-to-Image או Text-to-Image
                    if is_modification_request and last_image_url:
                        print("🔄 Using Image-to-Image mode with previous image")
                        print(f"📷 Base image URL: {last_image_url}")
                        
                        # Send to Flux Pro 1.1 with image input (Image-to-Image)
                        # Use lower strength to preserve shape/angle, change only color
                        image_url = send_flux_request(clean_prompt, replicate_api_key, init_image=last_image_url, strength=0.4)
                    else:
                        print("✨ Using Text-to-Image mode")
                        # Send to Flux Pro 1.1 (Text-to-Image)
                        image_url = send_flux_request(clean_prompt, replicate_api_key)
                    
                    # Download the image from Flux
                    img_response = requests.get(image_url, timeout=30)
                    if img_response.status_code == 200:
                        image_bytes = img_response.content
                        ai_service_name = "Flux Pro 1.1"
                    else:
                        raise Exception(f'Failed to download image from Flux URL: {img_response.status_code}')
                        
                elif freepik_api_key:
                    print("🎨 Using Freepik AI (fallback)")
                    
                    # Use Freepik AI as fallback
                    headers = {
                        'X-Freepik-API-Key': freepik_api_key,
                        'Content-Type': 'application/json'
                    }
                    
                    final_prompt = enhanced_prompt
                    clean_prompt = clean_prompt_for_ai(final_prompt)
                    
                    # בחירת API endpoint ו-payload לפי סוג הבקשה
                    if is_modification_request and last_image_url:
                        print("🔄 Using Freepik Image-to-Image mode")
                        print(f"📷 Base image URL: {last_image_url}")
                        
                        # שימוש ב-Image-to-Image API של Freepik
                        api_url = 'https://api.freepik.com/v1/ai/image-to-image'
                        payload = {
                            'prompt': clean_prompt,
                            'image': last_image_url,
                            'strength': 0.7,  # רמת השינוי (0.1=שינוי קל, 1.0=שינוי מלא)
                            'num_inference_steps': 50,
                            'guidance_scale': 7.5,
                            'num_images': 1
                        }
                    else:
                        print("✨ Using Freepik Text-to-Image mode")
                        # שימוש ב-Text-to-Image API רגיל של Freepik
                        api_url = 'https://api.freepik.com/v1/ai/text-to-image'
                        payload = create_freepik_payload(clean_prompt)
                    
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
                            'used_image_to_image': is_modification_request and bool(last_image_url),
                            'base_image_url': last_image_url if (is_modification_request and last_image_url) else None,
                            'modification_keywords_detected': [kw for kw in modification_keywords if kw in simple_prompt.lower()] if is_modification_request else []
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
                        'used_image_to_image': is_modification_request and bool(last_image_url),
                        'base_image_url': last_image_url if (is_modification_request and last_image_url) else None
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
