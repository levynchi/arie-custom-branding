from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='שם הקטגוריה')
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True, verbose_name='תיאור')
    is_active = models.BooleanField(default=True, verbose_name='פעיל')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'קטגוריה'
        verbose_name_plural = 'קטגוריות'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

class Product(models.Model):
    FABRIC_CHOICES = [
        ('cotton', 'כותנה'),
        ('polyester', 'פוליאסטר'),
        ('blend', 'תערובת'),
        ('bamboo', 'במבוק'),
        ('linen', 'פשתן'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='שם המוצר')
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='קטגוריה')
    description = models.TextField(verbose_name='תיאור')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='מחיר')
    fabric_type = models.CharField(max_length=20, choices=FABRIC_CHOICES, verbose_name='סוג בד')
    colors_available = models.JSONField(default=list, verbose_name='צבעים זמינים')
    sizes_available = models.JSONField(default=list, verbose_name='מידות זמינות')
    image = models.ImageField(upload_to='products/', verbose_name='תמונה ראשית')
    is_active = models.BooleanField(default=True, verbose_name='פעיל')
    is_featured = models.BooleanField(default=False, verbose_name='מוצר מומלץ')
    stock_quantity = models.IntegerField(default=0, verbose_name='כמות במלאי')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'מוצר'
        verbose_name_plural = 'מוצרים'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'תמונת מוצר'
        verbose_name_plural = 'תמונות מוצר'

class CustomDesign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='designs')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='designs', null=True, blank=True, verbose_name='מוצר')
    name = models.CharField(max_length=200, verbose_name='שם העיצוב')
    design_data = models.JSONField(verbose_name='נתוני עיצוב')  # Store design configuration
    preview_image = models.ImageField(upload_to='designs/previews/', blank=True, null=True)
    is_public = models.BooleanField(default=False, verbose_name='עיצוב ציבורי')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'עיצוב אישי'
        verbose_name_plural = 'עיצובים אישיים'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"

class BusinessQuote(models.Model):
    STATUS_CHOICES = [
        ('pending', 'ממתין'),
        ('in_progress', 'בעבודה'),
        ('completed', 'הושלם'),
        ('cancelled', 'בוטל'),
    ]
    
    company_name = models.CharField(max_length=200, verbose_name='שם החברה')
    contact_person = models.CharField(max_length=100, verbose_name='איש קשר')
    email = models.EmailField(verbose_name='אימייל')
    phone = models.CharField(max_length=20, verbose_name='טלפון')
    product_type = models.CharField(max_length=100, verbose_name='סוג מוצר')
    quantity = models.IntegerField(verbose_name='כמות')
    description = models.TextField(verbose_name='תיאור הצורך')
    logo_file = models.FileField(upload_to='business_quotes/logos/', blank=True, null=True, verbose_name='קובץ לוגו')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='סטטוס')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'בקשת הצעת מחיר עסקית'
        verbose_name_plural = 'בקשות הצעות מחיר עסקיות'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company_name} - {self.product_type}"
