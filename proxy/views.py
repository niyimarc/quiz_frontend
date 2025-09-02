import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .utils import generate_hmac_headers, refresh_access_token
from urllib.parse import urlencode

@csrf_exempt
def proxy_handler(request):
    endpoint = request.GET.get('endpoint')
    endpoint_type = request.GET.get('endpoint_type', 'private')
    # Sign the backend endpoint, including query string
    hmac_endpoint = endpoint
    query_params = request.GET.dict()
    if query_params:
        encoded_query = urlencode(query_params)
        hmac_endpoint = f"{endpoint}?{encoded_query}"

    if not endpoint:
        return JsonResponse({'error': 'Missing endpoint'}, status=400)

    backend_base_url = settings.BACKEND_BASE_URL
    full_url = f'{backend_base_url}{endpoint}'
    method = request.method

    # Function to prepare headers
    def build_headers(access_token=None):
        headers = generate_hmac_headers(hmac_endpoint)
        headers['X-API-KEY'] = settings.API_KEY

        if endpoint_type == 'private' and access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        if method in ['POST', 'PUT', 'PATCH']:
            headers['Content-Type'] = 'application/json'

        return headers

    # Build headers
    access_token = (
        request.headers.get('Authorization', '').replace('Bearer ', '') or 
        request.session.get('access_token')
    )

    headers = build_headers(access_token)
    data = request.body if method in ['POST', 'PUT', 'PATCH'] else None

    try:
        response = requests.request(method, full_url, headers=headers, params=query_params, data=data)

        # if response.status_code == 403:
        #     print("403 Forbidden Response:")
        #     print(response.text)

        # Token refresh logic
        if endpoint_type == 'private' and response.status_code in [401, 403]:
            try:
                error_data = response.json()
                if error_data.get('code') == 'token_not_valid':
                    # print("Access token expired or invalid. Attempting refresh...")
                    new_token = refresh_access_token(request.session)
                    # print(f"New Token: {new_token}")
                    if new_token:
                        headers = build_headers(new_token)
                        response = requests.request(method, full_url, headers=headers, params=query_params, data=data)
                    else:
                        return JsonResponse({'error': 'Session expired or token refresh failed.'}, status=401)
            except Exception as e:
                print("Error parsing response JSON or refreshing:", e)
                # Return the original response as fallback
                return HttpResponse(
                    response.content,
                    status=response.status_code,
                    content_type=response.headers.get('Content-Type', 'application/json')
                )

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'application/json')
        )

    except requests.RequestException as e:
        print("Proxy request failed:", e)
        return JsonResponse({'error': 'Request failed'}, status=502)