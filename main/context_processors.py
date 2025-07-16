from .models import Category

def categories_context(request):
    """Context processor להוספת קטגוריות לכל תמלטה"""
    categories = Category.objects.filter(is_active=True).order_by('name')
    return {
        'navbar_categories': categories
    }
