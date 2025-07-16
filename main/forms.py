from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('company_name', css_class='form-group col-md-6 mb-3'),
                Column('contact_person', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('phone', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('product_type', css_class='form-group col-md-6 mb-3'),
                Column('quantity', css_class='form-group col-md-6 mb-3'),
            ),
            'description',
            'logo_file',
            Submit('submit', 'שלח בקשה', css_class='btn btn-primary btn-lg mt-3')
        )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-3'),
                Column('subject', css_class='form-group col-md-6 mb-3'),
            ),
            'message',
            Submit('submit', 'שלח הודעה', css_class='btn btn-primary btn-lg mt-3')
        )
