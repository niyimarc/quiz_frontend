from django.shortcuts import render
from .utils import get_quizzes
from django.core.cache import cache
import requests
import json
# Create your views here.

def list_quiz(request):
    request.skip_quiz_categories_context = False
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    category_id = request.GET.get("category_id")
    search = request.GET.get("search", "")
    data = get_quizzes(request, category_id=category_id, page=page, search=search)

    return render(request, "list_quizzes.html", data)

def start_quiz(request, quiz_id):
    quiz_data = cache.get("quiz_data")
    try:
        access_token = request.session.get("access_token")
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        payload = json.dumps({"quiz_id": quiz_id})

        resp = requests.post(
            request.build_absolute_uri("/proxy/"),
            params={
                "endpoint": "/api/quiz/start_quiz/",
                "endpoint_type": "private"
            },
            data=payload,
            headers=headers,
            cookies={"sessionid": request.COOKIES.get("sessionid")},
            timeout=5
        )
        resp.raise_for_status()
        quiz_data = resp.json()
        cache.set("quiz_data", quiz_data, 60 * 30)  # cache for 30 mins
        # print("Fetched quiz data:", quiz_data)
    except Exception as e:
        quiz_data = []
        print("Error fetching quiz data:", e)

    return render(request, "quiz.html", {"quiz_data": quiz_data})
