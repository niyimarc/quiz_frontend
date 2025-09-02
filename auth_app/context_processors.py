def auth_status(request):
    return {
        'is_logged_in': 'access_token' in request.session,
        'user_profile': request.session.get('user_profile', {})
    }
