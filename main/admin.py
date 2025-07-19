from django.contrib import admin
from .models import Category, Product, ProductImage, CustomDesign, BusinessQuote, AIConversation, AIMessage

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
    list_display = ['name', 'category', 'price', 'fabric_type', 'can_print', 'max_print_width', 'max_print_height', 'is_active', 'is_featured', 'stock_quantity']
    list_filter = ['category', 'fabric_type', 'can_print', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    list_editable = ['can_print', 'max_print_width', 'max_print_height', 'is_active', 'is_featured', 'stock_quantity']
    
    fieldsets = (
        ('מידע כללי', {
            'fields': ('name', 'slug', 'category', 'description', 'image')
        }),
        ('מחיר ומלאי', {
            'fields': ('price', 'stock_quantity')
        }),
        ('מפרט מוצר', {
            'fields': ('fabric_type', 'colors_available', 'sizes_available')
        }),
        ('הדפסה', {
            'fields': ('can_print', 'max_print_width', 'max_print_height'),
            'description': 'מידות הדפסה מקסימליות בסנטימטרים'
        }),
        ('הגדרות', {
            'fields': ('is_active', 'is_featured')
        }),
    )

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


class AIMessageInline(admin.TabularInline):
    model = AIMessage
    extra = 0
    readonly_fields = ['created_at']
    fields = ['message_type', 'content', 'translated_prompt', 'ai_service_used', 'created_at']


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user_display', 'product', 'message_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'product__category']
    search_fields = ['title', 'user__username', 'session_id', 'product__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [AIMessageInline]
    
    def user_display(self, obj):
        if obj.user:
            return obj.user.username
        return f"Anonymous ({obj.session_id[:8]}...)"
    user_display.short_description = 'משתמש'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'מספר הודעות'


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'message_type', 'content_preview', 'ai_service_used', 'created_at']
    list_filter = ['message_type', 'ai_service_used', 'created_at']
    search_fields = ['content', 'translated_prompt', 'conversation__title']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'תוכן'
