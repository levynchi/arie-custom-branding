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
            
            # Build enhanced prompt for the AI
            enhanced_prompt = f"""
            Create a high-quality graphic design element only (NOT the product itself) based on: {prompt}
            
            IMPORTANT REQUIREMENTS:
            1. Create ONLY the graphic/design element - DO NOT include the product (bag, hat, shirt, etc.)
            2. If user mentions a product (bag, hat, shirt, etc.), create only the graphic that would go ON that product
            3. Maximum dimensions: 396.8 pixels width x 453.5 pixels height
            4. PNG format with transparent background (no background at all)
            5. Ultra-high quality and sharp details for printing
            6. High contrast design suitable for textile printing
            7. Professional and clean design
            8. Vector-style or high-resolution graphic suitable for screen printing
            
            Examples:
            - If user says "logo for a bag" → create only the logo graphic, not the bag
            - If user says "design for a hat" → create only the design graphic, not the hat
            - If user says "text for a shirt" → create only the text graphic, not the shirt
            
            Create a standalone graphic design element that can be printed on any product.
            Focus on the graphic content only, with transparent background, optimized for printing.
            """
            
            # Generate image using OpenAI DALL-E API
            try:
                # Note: You'll need to get an OpenAI API key and add it to settings
                api_key = getattr(settings, 'OPENAI_API_KEY', None)
                if not api_key:
                    return JsonResponse({
                        'success': False, 
                        'error': 'AI service not configured. Please contact administrator.'
                    })
                
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'model': 'dall-e-3',
                    'prompt': enhanced_prompt,
                    'n': 1,
                    'size': '1024x1024',  # OpenAI supports: 1024x1024, 1792x1024, 1024x1792
                    'quality': 'hd',      # Changed to 'hd' for higher quality
                    'response_format': 'url'
                }
                
                response = requests.post(
                    'https://api.openai.com/v1/images/generations',
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_url = result['data'][0]['url']
                    
                    # Download the generated image
                    image_response = requests.get(image_url, timeout=30)
                    if image_response.status_code == 200:
                        # Process the image to resize it to the required dimensions
                        try:
                            # Open the image with PIL
                            image = Image.open(io.BytesIO(image_response.content))
                            
                            # Convert to RGBA to ensure transparency support
                            if image.mode != 'RGBA':
                                image = image.convert('RGBA')
                            
                            # Resize to the specified dimensions (396.8 x 453.5 pixels)
                            # Round to nearest integer pixels
                            target_size = (397, 454)  # Rounded from 396.8 x 453.5
                            
                            # Resize with high quality resampling
                            image = image.resize(target_size, Image.Resampling.LANCZOS)
                            
                            # Save the processed image to a BytesIO buffer
                            output_buffer = io.BytesIO()
                            image.save(output_buffer, format='PNG', optimize=True, quality=100)
                            output_buffer.seek(0)
                            
                            # Create unique filename
                            filename = f"ai_design_{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                            
                            # Save to media directory
                            file_path = os.path.join('ai_designs', filename)
                            saved_path = default_storage.save(file_path, ContentFile(output_buffer.getvalue()))
                            
                            # Get full URL
                            full_url = request.build_absolute_uri(default_storage.url(saved_path))
                            
                            return JsonResponse({
                                'success': True,
                                'image_url': full_url,
                                'filename': filename,
                                'dimensions': f'{target_size[0]}x{target_size[1]} pixels'
                            })
                            
                        except Exception as img_error:
                            return JsonResponse({
                                'success': False,
                                'error': f'Image processing error: {str(img_error)}'
                            })
                    else:
                        return JsonResponse({
                            'success': False,
                            'error': 'Failed to download generated image'
                        })
                else:
                    error_msg = response.json().get('error', {}).get('message', 'Unknown API error')
                    return JsonResponse({
                        'success': False,
                        'error': f'AI service error: {error_msg}'
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
