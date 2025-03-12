from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import AuthenticationForm
from .forms import (
    CustomUserRegistrationForm, UpdateUserForm, UpdateUserPassword, 
    UpdateInfoForm, ShippingAddressForm
)
from .models import CustomUser, Profile, ShippingAddress
import json
from cart.cart import Cart

# Register User with Referral System# Register User with Referral System
def register_user(request):
    # Check if referral ID is in GET request and store it in session
    if 'ref' in request.GET:
        referral_id = request.GET.get('ref')
        request.session['referral_id'] = referral_id  # Store in session
        print(f"Referral ID received and stored in session: {referral_id}")

    # Retrieve referral ID from session (if available)
    referral_id = request.session.get('referral_id')
    print(f"Referral ID used for registration: {referral_id}")  # Debugging

    parent_sponsor = None
    if referral_id:
        try:
            parent_sponsor = CustomUser.objects.get(unique_id=referral_id)
            print(f"Parent Sponsor Found: {parent_sponsor.email}")  # Debugging
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid referral link.")
            return redirect('register')

    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.parent_sponsor = parent_sponsor  # Assign sponsor
            user.save()
            print(f"User {user.email} saved with Parent Sponsor: {user.parent_sponsor.email if user.parent_sponsor else 'None'}")  # Debugging
            
            # Clear the referral ID from session after use
            request.session.pop('referral_id', None)

            login(request, user)
            messages.success(request, 'Registration successful. Please fill in your shipping info.')
            return redirect('update_info')
        else:
            messages.error(request, 'Unsuccessful registration. Invalid information.')
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


# Login User
def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                # Restore previous cart
                current_user = Profile.objects.get(user=request.user)
                saved_cart = current_user.old_cart
                if saved_cart:
                    cart = Cart(request)
                    for key, value in json.loads(saved_cart).items():
                        cart.db_add(product=key, quantity=value)

                messages.success(request, 'Login successful!')
                return redirect('home')
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})

# Logout User
def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out!')
    return redirect('home')

# Update User
def update_user(request):
    if request.user.is_authenticated:
        user_form = UpdateUserForm(request.POST or None, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'User details updated.')
            return redirect('home')
        return render(request, 'users/update_user.html', {'user_form': user_form})
    messages.error(request, "You must be logged in to update your details.")
    return redirect('home')

# Update User Profile Info
def update_info(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        form = UpdateInfoForm(request.POST or None, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile info has been updated.")
            return redirect('home')
        return render(request, 'users/update_info.html', {'form': form})
    messages.error(request, "You must be logged in to update your info.")
    return redirect('login')

# Update User Password
def update_password(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = UpdateUserPassword(request.user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been updated. Log in with your new password.")
                return redirect('login')
            messages.error(request, "Please correct the errors below.")
        else:
            form = UpdateUserPassword(request.user)
        return render(request, 'users/update_password.html', {'form': form})
    messages.error(request, "You must be logged in to update your password.")
    return redirect('home')

# User Profile View
def user_profile(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        user_data = {
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'unique_id': request.user.unique_id,
            'referral_link': f"{request.scheme}://{request.get_host()}/users/register/?ref={request.user.unique_id}",
            'parent_sponsor': request.user.parent_sponsor.unique_id if request.user.parent_sponsor else "None"
        }
        return render(request, 'users/user_profile.html', {'user_data': user_data})
    messages.error(request, "You must be logged in to view your profile.")
    return redirect('login')

# Shipping Information View
def shipping_info(request):
    if request.user.is_authenticated:
        shipping_address, created = ShippingAddress.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            form = ShippingAddressForm(request.POST, instance=shipping_address)
            if form.is_valid():
                form.save()
                messages.success(request, "Your shipping information has been updated.")
                return redirect('home')
        else:
            form = ShippingAddressForm(instance=shipping_address)
        return render(request, 'users/shipping_information.html', {'form': form})
    messages.error(request, "You must be logged in to update your info.")
    return redirect('login')

# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        if not CustomUser.objects.filter(email=email).exists():
            messages.error(self.request, "This email address is not registered.")
            return self.form_invalid(form)
        return super().form_valid(form)

class PasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'

class PasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class PasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'
