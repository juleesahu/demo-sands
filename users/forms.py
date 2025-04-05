from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django import forms
from .models import CustomUser, Profile, ShippingAddress


class CustomUserCreationForm(UserCreationForm):
    """Form for Django admin user creation"""
    unique_id = forms.CharField(max_length=50, required=False, disabled=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = CustomUser
        fields = ("email", "unique_id")


class CustomUserChangeForm(UserChangeForm):
    """Form for Django admin user updates"""
    unique_id = forms.CharField(max_length=50, required=False, disabled=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = CustomUser
        fields = ("email", "unique_id")


class CustomUserRegistrationForm(UserCreationForm):
    """Form for user registration with additional required fields"""
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email',  'password1', 'password2')

    def clean_email(self):
        """Ensure the email is unique"""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class UpdateUserForm(UserChangeForm):
    """Form for updating user details without changing password"""
    password = None  # Hide password field

    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    unique_id = forms.CharField(max_length=50, required=False, disabled=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'unique_id']

    def clean_email(self):
        """Ensure the email remains unique when updating"""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class UpdateUserPassword(PasswordChangeForm):
    """Form for changing user password with improved placeholders"""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Current Password'}), 
        label="Current Password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}), 
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}), 
        label="Confirm New Password"
    )


class UpdateInfoForm(forms.ModelForm):
    """Form for updating user profile information"""
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone'}))
    address1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Address 1'}))
    address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Address 2'}))
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'City'}))
    state = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'State'}))
    zipcode = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Zip Code'}))
    country = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Country'}))

    class Meta:
        model = Profile
        fields = ["phone", "address1", "address2", "city", "state", "zipcode", "country"]


class ShippingAddressForm(forms.ModelForm):
    """Form for adding/updating a shipping address"""
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone'}))
    address1 = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Address 1'}))
    address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Address 2'}))
    city = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'City'}))
    state = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'State'}))
    zipcode = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Zip Code'}))
    country = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Country'}))

    class Meta:
        model = ShippingAddress
        fields = ["phone", "address1", "address2", "city", "state", "zipcode", "country"]
