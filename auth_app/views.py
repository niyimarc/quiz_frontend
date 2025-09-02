from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
import requests
from .utils import redirect_if_authenticated

@redirect_if_authenticated
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Build proxy handler URL
        proxy_url = request.build_absolute_uri(
            reverse('proxy_handler') + '?endpoint=/api/login/&endpoint_type=public'
        )

        # Forward request to proxy handler
        response = requests.post(
            proxy_url,
            json={'username': username, 'password': password}
        )

        if response.status_code == 200:
            tokens = response.json()

            access_token = tokens.get('access')
            refresh_token = tokens.get('refresh')

            request.session['access_token'] = tokens.get('access')
            request.session['refresh_token'] = tokens.get('refresh')

            # Fetch and store user profile
            profile_url = request.build_absolute_uri(
                reverse('proxy_handler') + '?endpoint=/api/user/profile/&endpoint_type=private'
            )
            try:
                sessionid = request.COOKIES.get('sessionid')
                profile_response = requests.get(
                    profile_url,
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Cookie': f'sessionid={sessionid}'
                    }
                )
                if profile_response.status_code == 200:
                    request.session['user_profile'] = profile_response.json()
                    request.session.save()
            except requests.RequestException:
                request.session['user_profile'] = {}

            guest_cart = request.session.get('cart', [])
            if guest_cart:
                sync_cart_url = request.build_absolute_uri(
                    reverse('proxy_handler') + '?endpoint=/api/cart/sync_cart/&endpoint_type=private'
                )

                sessionid = request.COOKIES.get('sessionid')

                try:
                    sync_response = requests.post(
                        sync_cart_url,
                        json={'cart_items': guest_cart},
                        headers={
                            'Authorization': f'Bearer {access_token}',
                            'Cookie': f'sessionid={sessionid}'
                        }
                    )
                    if sync_response.status_code == 200:
                        del request.session['cart']  # Clear guest cart after sync
                except requests.RequestException as e:
                    print("Cart sync failed:", str(e))

            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect('store:home')
        else:
            messages.error(request, 'Invalid credentials.')

    return render(request, 'login.html', {
            "next": request.GET.get("next", "")
        })

@redirect_if_authenticated
def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            print("Passwords do not match.")
            return render(request, 'auth/register.html')

        proxy_url = request.build_absolute_uri(
            reverse('proxy_handler') + '?endpoint=/api/register/&endpoint_type=public'
        )

        response = requests.post(
            proxy_url,
            json={'username': username, 'password': password, 'email': email, 'first_name': first_name, 'last_name': last_name}
        )

        if response.status_code == 201:
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('auth_app:login')
        else:
            messages.error(request, 'Registration failed.')

    return render(request, 'register.html')

def logout_view(request):
    proxy_url = request.build_absolute_uri(
        reverse('proxy_handler') + '?endpoint=/api/logout/&endpoint_type=private'
    )

    refresh_token = request.session.get('refresh_token')
    access_token = request.session.get('access_token')
    if refresh_token and access_token:
        # Attempt logout via backend
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            requests.post(proxy_url, json={'refresh': refresh_token}, headers=headers)
        except requests.RequestException:
            pass  # Ignore any logout errors silently

    # Clear session and redirect to login regardless
    request.session.flush()
    return redirect('auth_app:login')