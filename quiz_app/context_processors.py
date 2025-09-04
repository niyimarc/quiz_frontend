from django.conf import settings
import requests
from django.urls import reverse
from django.core.cache import cache

def app_information(request):
    return {
        "business_name": settings.BUSINESS_NAME,
        "business_logo": settings.BUSINESS_LOGO,
        "contact_email": settings.CONTACT_EMAIL,
    }

def quiz_categories_data(request):
    # Skip if the view has set this flag
    if getattr(request, "skip_quiz_categories_context", False):
        return {}
    
    quiz_categories = cache.get("quiz_categories_data")
    # quiz_categories = []
    if not quiz_categories:
        try:
            access_token = request.session.get("access_token")
            headers = {}
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"

            resp = requests.get(
                request.build_absolute_uri("/proxy/"),
                params={
                    "endpoint": "/api/quiz/categories_with_quizzes/",
                    "endpoint_type": "private"
                },
                headers=headers,
                cookies={"sessionid": request.COOKIES.get("sessionid")},
                timeout=5
            )
            resp.raise_for_status()
            quiz_categories = resp.json()
            cache.set("quiz_categories_data", quiz_categories, 60 * 30)  # cache for 30 mins
            # print("Fetched categories:", quiz_categories)
        except Exception as e:
            quiz_categories = []
            print("Error fetching categories:", e)

    return {"quiz_categories": quiz_categories}
