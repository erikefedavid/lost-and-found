from django import forms
from django.core.validators import MinLengthValidator
from .models import User, LostItem, FoundItem, Claim

INPUT_CLASSES = 'w-full px-5 py-4 bg-slate-50 border border-slate-100 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-[#003366]/10 focus:bg-white placeholder:text-slate-300 transition-all'

class UserRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(validators=[MinLengthValidator(3)], widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Enter your full name'}))
    password = forms.CharField(validators=[MinLengthValidator(6)], widget=forms.PasswordInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Create a strong password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Confirm your password'}))

    class Meta:
        model = User
        fields = ['full_name', 'email', 'campus_id']
        widgets = {
            'email': forms.EmailInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Enter your university email'}),
            'campus_id': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Optional (e.g. LCU/2023/...) '}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class LostItemForm(forms.ModelForm):
    item_name = forms.CharField(validators=[MinLengthValidator(2)], widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'What did you lose?'}))
    description = forms.CharField(validators=[MinLengthValidator(10)], widget=forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 4, 'placeholder': 'Provide details (color, brand, serial number...)'}))
    
    class Meta:
        model = LostItem
        fields = ['item_name', 'description', 'category', 'location', 'date_lost', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': INPUT_CLASSES}),
            'location': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Where was it last seen?'}),
            'date_lost': forms.DateInput(attrs={'class': INPUT_CLASSES, 'type': 'date'}),
            'image': forms.FileInput(attrs={'class': 'w-full px-5 py-4 bg-slate-50 border border-slate-100 rounded-2xl text-sm file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-bold file:bg-[#003366] file:text-white hover:file:bg-[#002244]'}),
        }
        help_texts = {
            'image': '💡 Tip: Items with clear photos are recovered 3x faster!',
        }

class FoundItemForm(forms.ModelForm):
    item_name = forms.CharField(validators=[MinLengthValidator(2)], widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'What did you find?'}))
    description = forms.CharField(validators=[MinLengthValidator(10)], widget=forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 4, 'placeholder': 'Describe the item (be careful not to give away secrets)'}))

    class Meta:
        model = FoundItem
        fields = ['item_name', 'description', 'category', 'location', 'date_found', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': INPUT_CLASSES}),
            'location': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Where did you find it?'}),
            'date_found': forms.DateInput(attrs={'class': INPUT_CLASSES, 'type': 'date'}),
            'image': forms.FileInput(attrs={'class': 'w-full px-5 py-4 bg-slate-50 border border-slate-100 rounded-2xl text-sm file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-bold file:bg-[#003366] file:text-white hover:file:bg-[#002244]'}),
        }
        help_texts = {
            'image': '💡 Tip: Uploading an image makes it easier for the owner to identify it!',
        }

class ClaimForm(forms.ModelForm):
    justification = forms.CharField(validators=[MinLengthValidator(20)], widget=forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 3, 'placeholder': 'Describe specific details only the owner would know (e.g. passwords, specific marks, contents)...'}))
    
    class Meta:
        model = Claim
        fields = ['justification']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'campus_id']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Enter your full name'}),
            'campus_id': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. LCU/2023/...'}),
        }

