from django import forms
from .models import BusinessQuote

class BusinessQuoteForm(forms.ModelForm):
    class Meta:
        model = BusinessQuote
        fields = ['company_name', 'contact_person', 'email', 'phone', 'product_type', 'quantity', 'description', 'logo_file']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'שם החברה'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'שם מלא'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '050-1234567'}),
            'product_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'חולצות, בגדי תינוקות, מגבות וכו׳'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'כמות מוצרים'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'תארו את הצורך שלכם, צבעים רצויים, הדפסות וכו׳'}),
            'logo_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'company_name': 'שם החברה *',
            'contact_person': 'איש קשר *',
            'email': 'אימייל *',
            'phone': 'טלפון *',
            'product_type': 'סוג המוצר *',
            'quantity': 'כמות *',
            'description': 'תיאור הצורך *',
            'logo_file': 'קובץ לוגו (אופציונלי)',
        }

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='שם מלא *',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'שם מלא'})
    )
    email = forms.EmailField(
        label='אימייל *',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com'})
    )
    phone = forms.CharField(
        max_length=20,
        label='טלפון',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '050-1234567'})
    )
    subject = forms.CharField(
        max_length=200,
        label='נושא *',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'נושא ההודעה'})
    )
    message = forms.CharField(
        label='הודעה *',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'כתוב את הודעתך כאן...'})
    )
