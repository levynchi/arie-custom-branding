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
