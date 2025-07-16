from django.contrib import admin
from .models import Category, Product, ProductImage, CustomDesign, BusinessQuote

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'fabric_type', 'is_active', 'is_featured', 'stock_quantity']
    list_filter = ['category', 'fabric_type', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    list_editable = ['is_active', 'is_featured', 'stock_quantity']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_main']
    list_filter = ['is_main', 'product__category']

@admin.register(CustomDesign)
class CustomDesignAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'user__username']

@admin.register(BusinessQuote)
class BusinessQuoteAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'contact_person', 'email', 'product_type', 'quantity', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'product_type']
    search_fields = ['company_name', 'contact_person', 'email']
    list_editable = ['status']
    readonly_fields = ['created_at']
