from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
from .models import Category, Product, BusinessQuote, CustomDesign
from .forms import BusinessQuoteForm, ContactForm

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
    """יצירת עיצוב באמצעות AI"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '')
            product_id = data.get('product_id', '')
            product_name = data.get('product_name', '')
            
            if not prompt:
                return JsonResponse({'success': False, 'error': 'חסר תיאור עיצוב'})
            
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
                except Product.DoesNotExist:
                    pass
            
            # Build very simple prompt for accurate results - translate Hebrew to English
            # First, translate Hebrew text to English using OpenAI
            def translate_hebrew_to_english(text):
                """Translate Hebrew text to English using OpenAI API"""
                try:
                    openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
                    if not openai_api_key:
                        print("⚠️ DEBUG: OpenAI API key not found, using fallback translation")
                        # Fallback to simple dictionary
                        hebrew_translations = {
                            'בננה': 'banana',
                            'תפוח': 'apple',
                            'עוגה': 'cake',
                            'פרח': 'flower',
                            'עץ': 'tree',
                            'בית': 'house',
                            'כלב': 'dog',
                            'חתול': 'cat',
                            'שמש': 'sun',
                            'ירח': 'moon',
                            'לוגו': 'logo',
                            'אקרובטית': 'acrobat',
                            'כיתוב': 'text',
                            'רוצה': 'want',
                            'תייצר': 'create',
                            'של': 'of'
                        }
                        
                        # Try to find Hebrew words in the text
                        for hebrew_word, english_word in hebrew_translations.items():
                            if hebrew_word in text:
                                return english_word
                        return text
                    
                    # Use OpenAI for translation
                    headers = {
                        'Authorization': f'Bearer {openai_api_key}',
                        'Content-Type': 'application/json'
                    }
                    
                    payload = {
                        'model': 'gpt-3.5-turbo',
                        'messages': [
                            {
                                'role': 'system',
                                'content': 'You are a translator. Translate Hebrew text to English completely and accurately. Preserve all details from the original text including specific requests for logos, text content, and design elements. Translate the entire sentence, not just the main object.'
                            },
                            {
                                'role': 'user',
                                'content': f'Translate this Hebrew text to English completely: "{text}"'
                            }
                        ],
                        'max_tokens': 150,  # Increased to allow longer translations
                        'temperature': 0.1
                    }
                    
                    response = requests.post(
                        'https://api.openai.com/v1/chat/completions',
                        headers=headers,
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        translated_text = result['choices'][0]['message']['content'].strip()
                        print(f"🌐 DEBUG: OpenAI translation: '{text}' → '{translated_text}'")
                        return translated_text
                    else:
                        print(f"⚠️ DEBUG: OpenAI API error: {response.status_code}")
                        return text
                        
                except Exception as e:
                    print(f"⚠️ DEBUG: Translation error: {str(e)}")
                    return text
            
            # Check if the prompt is a Hebrew word we can translate
            simple_prompt = prompt.strip()
            print(f"🔍 DEBUG: Original prompt from user: '{prompt}'")
            print(f"🔍 DEBUG: Cleaned prompt: '{simple_prompt}'")
            
            # Try to translate Hebrew to English
            enhanced_prompt = translate_hebrew_to_english(simple_prompt)
            print(f"✅ DEBUG: Final translated prompt: '{enhanced_prompt}'")
            
            # Check for text/typography requests and extract text content
            def extract_text_requests(prompt):
                """Extract text content from prompts that request typography/logos with text"""
                import re
                
                # Patterns to detect text requests
                text_patterns = [
                    r'with.*?text[:\s]*["\']([^"\']+)["\']',  # with text: "content"
                    r'with.*?writing[:\s]*["\']([^"\']+)["\']',  # with writing: "content"
                    r'עם.*?כיתוב[:\s]*["\']([^"\']+)["\']',  # Hebrew: עם כיתוב: "content"
                    r'כיתוב[:\s]*:?[:\s]*([^,\.]+)',  # Hebrew: כיתוב: content
                    r'text[:\s]*:?[:\s]*([A-Z\s]+)',  # text: CONTENT
                    r'כיתוב\s+של\s+(.+?)(?:\s*$|\s*[,.;])',  # Hebrew: כיתוב של content
                    r'with\s+text\s+of\s+(.+?)(?:\s*$|\s*[,.;])',  # with text of content
                    r'text\s+of\s+(.+?)(?:\s*$|\s*[,.;])',  # text of content
                    r'עם\s+כיתוב\s+של\s+(.+?)(?:\s*$|\s*[,.;])',  # עם כיתוב של content
                ]
                
                extracted_texts = []
                visual_prompt = prompt
                
                for pattern in text_patterns:
                    matches = re.findall(pattern, prompt, re.IGNORECASE)
                    for match in matches:
                        text_content = match.strip()
                        if text_content and len(text_content) > 1:
                            extracted_texts.append(text_content)
                            # Remove the text specification from the visual prompt
                            visual_prompt = re.sub(pattern, '', visual_prompt, flags=re.IGNORECASE)
                
                # Clean up the visual prompt
                visual_prompt = re.sub(r'with\s+text\s*:?\s*', '', visual_prompt, flags=re.IGNORECASE)
                visual_prompt = re.sub(r'עם\s+כיתוב\s*:?\s*', '', visual_prompt, flags=re.IGNORECASE)
                visual_prompt = re.sub(r'כיתוב\s+של\s+.+', '', visual_prompt, flags=re.IGNORECASE)
                visual_prompt = re.sub(r'with\s+text\s+of\s+.+', '', visual_prompt, flags=re.IGNORECASE)
                visual_prompt = re.sub(r'text\s+of\s+.+', '', visual_prompt, flags=re.IGNORECASE)
                visual_prompt = re.sub(r'עם\s+כיתוב\s+של\s+.+', '', visual_prompt, flags=re.IGNORECASE)
                visual_prompt = re.sub(r'logo\s+of\s+', '', visual_prompt, flags=re.IGNORECASE)
                visual_prompt = visual_prompt.strip()
                
                return extracted_texts, visual_prompt
            
            # Extract text requests from the prompt
            extracted_texts, visual_only_prompt = extract_text_requests(enhanced_prompt)
            
            if extracted_texts:
                print(f"📝 DEBUG: Extracted text content: {extracted_texts}")
                print(f"🎨 DEBUG: Visual-only prompt: '{visual_only_prompt}'")
                
                # Generate text design using OpenAI for typography
                def generate_text_design(text_content):
                    """Generate SVG text design using OpenAI"""
                    try:
                        openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
                        if not openai_api_key:
                            return None
                        
                        headers = {
                            'Authorization': f'Bearer {openai_api_key}',
                            'Content-Type': 'application/json'
                        }
                        
                        payload = {
                            'model': 'gpt-4',
                            'messages': [
                                {
                                    'role': 'system',
                                    'content': 'You are a typography designer. Create clean SVG code for text designs. Return only valid SVG code with proper text elements, fonts, and styling. Make it professional and print-ready.'
                                },
                                {
                                    'role': 'user',
                                    'content': f'Create a clean, professional SVG design for the text: "{text_content}". Make it bold, readable, and suitable for printing on products. Use appropriate font sizes and styling.'
                                }
                            ],
                            'max_tokens': 1000,
                            'temperature': 0.3
                        }
                        
                        response = requests.post(
                            'https://api.openai.com/v1/chat/completions',
                            headers=headers,
                            json=payload,
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            svg_content = result['choices'][0]['message']['content'].strip()
                            print(f"🎨 DEBUG: Generated SVG typography: {svg_content[:100]}...")
                            return svg_content
                        else:
                            print(f"⚠️ DEBUG: OpenAI typography API error: {response.status_code}")
                            return None
                            
                    except Exception as e:
                        print(f"⚠️ DEBUG: Typography generation error: {str(e)}")
                        return None
                
                # Generate typography for the extracted texts
                text_designs = []
                for text in extracted_texts:
                    svg_design = generate_text_design(text)
                    if svg_design:
                        text_designs.append({
                            'text': text,
                            'svg': svg_design
                        })
                
                # If we have both visual elements and text, create combined design
                if visual_only_prompt and len(visual_only_prompt) > 2:
                    enhanced_prompt = visual_only_prompt
                    print(f"🔄 DEBUG: Will generate visual element separately and combine with text")
                else:
                    # If it's only text, return the typography design
                    if text_designs:
                        return JsonResponse({
                            'success': True,
                            'text_design': True,
                            'text_content': extracted_texts,
                            'svg_designs': text_designs,
                            'message': 'עוצב טקסט בלבד. ניתן להוסיף אלמנטים ויזואליים נוספים.'
                        })
            
            print(f"🎯 DEBUG: Final prompt for image generation: '{enhanced_prompt}'")
            
            # Generate image using Stability AI (Stable Diffusion XL)
            try:
                # Note: You'll need to get a Stability AI API key and add it to settings
                api_key = getattr(settings, 'STABILITY_API_KEY', None)
                
                # Debug: Print API key status
                print(f"Stability API Key status: {'Found' if api_key else 'Not found'}")
                print(f"API Key length: {len(api_key) if api_key else 0}")
                
                if not api_key:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Stability AI service not configured. Please add STABILITY_API_KEY to your .env file.'
                    })
                
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                
                # Stability AI payload for SDXL - ultra simplified for exact literal results
                # Check if the prompt contains numbers and make it more specific
                if any(char.isdigit() for char in enhanced_prompt):
                    # If there's a number, be very explicit about "exactly X items"
                    import re
                    numbers = re.findall(r'\d+', enhanced_prompt)
                    if numbers:
                        number = numbers[0]
                        item = re.sub(r'\d+\s*', '', enhanced_prompt).strip()
                        final_prompt = f"exactly {number} {item}, isolated on white background, simple illustration"
                    else:
                        final_prompt = f"a {enhanced_prompt} on white background"
                # For visual elements (text already extracted), create clean visual design
                else:
                    if not enhanced_prompt or len(enhanced_prompt) < 3:
                        enhanced_prompt = "simple minimalist design"
                    final_prompt = f"a {enhanced_prompt}, clean vector style, isolated on white background"
                
                print(f"🚀 DEBUG: Final prompt being sent to Stability AI: '{final_prompt}'")
                
                payload = {
                    'text_prompts': [
                        {
                            'text': final_prompt,
                            'weight': 1.0
                        }
                    ],
                    'cfg_scale': 5,  # Very low for literal interpretation
                    'height': 1024,
                    'width': 1024,
                    'samples': 1,
                    'steps': 20  # Minimal steps for simple, direct results
                }
                
                print(f"📦 DEBUG: Full payload: {payload}")
                print(f"🌐 DEBUG: Sending request to Stability AI...")
                
                response = requests.post(
                    'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
                    headers=headers,
                    json=payload,
                    timeout=60  # Increased timeout to 60 seconds
                )
                
                print(f"📡 DEBUG: Response status code: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"✅ DEBUG: Success! Image generated successfully")
                    result = response.json()
                    # Stability AI returns images in artifacts array
                    if 'artifacts' in result and len(result['artifacts']) > 0:
                        # The image is base64 encoded
                        image_data = result['artifacts'][0]['base64']
                        
                        # Decode base64 image
                        image_bytes = base64.b64decode(image_data)
                        
                        # Process the image directly from bytes
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
                            
                            # Save PNG version to media directory
                            png_file_path = os.path.join('ai_designs', png_filename)
                            png_saved_path = default_storage.save(png_file_path, ContentFile(output_buffer.getvalue()))
                            
                            # Save CMYK version to media directory
                            cmyk_file_path = os.path.join('ai_designs', cmyk_filename)
                            cmyk_saved_path = default_storage.save(cmyk_file_path, ContentFile(cmyk_buffer.getvalue()))
                            
                            # Get full URLs
                            png_url = request.build_absolute_uri(default_storage.url(png_saved_path))
                            cmyk_url = request.build_absolute_uri(default_storage.url(cmyk_saved_path))
                            
                            response_data = {
                                'success': True,
                                'image_url': png_url,
                                'cmyk_url': cmyk_url,
                                'filename': png_filename,
                                'cmyk_filename': cmyk_filename,
                                'dimensions': f'{target_size[0]}x{target_size[1]} pixels',
                                'dpi': '300 DPI',
                                'max_print_size': f'{max_width/118.11:.1f}x{max_height/118.11:.1f} cm'
                            }
                            
                            # Add text designs if any were generated
                            if 'text_designs' in locals() and text_designs:
                                response_data['text_designs'] = text_designs
                                response_data['has_text'] = True
                                response_data['message'] = 'נוצרו גם עיצובי טקסט נפרדים שניתן לשלב עם התמונה'
                            
                            return JsonResponse(response_data)
                            
                        except Exception as img_error:
                            return JsonResponse({
                                'success': False,
                                'error': f'Image processing error: {str(img_error)}'
                            })
                    else:
                        return JsonResponse({
                            'success': False,
                            'error': 'No artifacts in Stability AI response'
                        })
                else:
                    try:
                        error_response = response.json()
                        error_msg = error_response.get('message', 'Unknown Stability AI error')
                        error_id = error_response.get('id', 'unknown')
                        
                        # Log detailed error information
                        print(f"Stability AI API Error: {error_id} - {error_msg}")
                        print(f"Response status: {response.status_code}")
                        print(f"Response text: {response.text}")
                        
                        return JsonResponse({
                            'success': False,
                            'error': f'Stability AI service error: {error_msg}',
                            'error_code': error_id,
                            'status_code': response.status_code
                        })
                    except:
                        return JsonResponse({
                            'success': False,
                            'error': f'Stability AI service error: HTTP {response.status_code} - {response.text}'
                        })
                    
            except requests.exceptions.RequestException as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Network error: {str(e)}'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Unexpected error: {str(e)}'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
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
