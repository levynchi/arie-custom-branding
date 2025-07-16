from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:category_slug>/', views.category_products, name='category_products'),
    path('business-quote/', views.business_quote, name='business_quote'),
    path('custom-design/', views.custom_design, name='custom_design'),
    path('save-design/', views.save_design, name='save_design'),
    path('generate-ai-design/', views.generate_ai_design, name='generate_ai_design'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
