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
    path('custom_design/', views.custom_design, name='custom_design_underscore'),  # גם עם תחתון
    path('save-design/', views.save_design, name='save_design'),
    path('generate-ai-design/', views.generate_ai_design, name='generate_ai_design'),
    path('search-freepik-images/', views.search_freepik_images, name='search_freepik_images'),
    path('download-freepik-image/', views.download_freepik_image, name='download_freepik_image'),
    path('ai-conversations/', views.get_ai_conversations, name='get_ai_conversations'),
    path('conversation-history/', views.get_conversation_history, name='get_conversation_history'),
    path('ai-conversation-demo/', views.ai_conversation_demo, name='ai_conversation_demo'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
