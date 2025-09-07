from django.shortcuts import render
from .utils import get_quizzes, get_retryable_quizzes
from auth_app.utils import session_access_required
from django.core.cache import cache
import requests
import json

@session_access_required
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

@session_access_required
def start_quiz(request, quiz_id):
    quiz_data = None

    try:
        access_token = request.session.get("access_token")
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        # First, try to get cached quiz_data (if any active session already cached)
        # We don't know session_id yet, so just check the old cache key
        quiz_data = cache.get(f"quiz_data_{request.user.id}_{quiz_id}")

        if not quiz_data:
            # Start a new quiz session
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

            # Now that we have session_id, build unique cache key
            session_id = quiz_data.get("session_id")
            cache_key = f"quiz_data_{request.user.id}_{quiz_id}_{session_id}"
            # print(cache_key)

            cache.set(cache_key, quiz_data, 60 * 60)  # cache for 60 mins

    except Exception as e:
        quiz_data = []

    return render(request, "quiz.html", {"quiz_data": quiz_data})


@session_access_required
def continue_quiz_view(request):
    quiz_data = []
    try:
        access_token = request.session.get("access_token")
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        # GET request to proxy
        resp = requests.get(
            request.build_absolute_uri("/proxy/"),
            params={
                "endpoint": "/api/quiz/continue_session/",
                "endpoint_type": "private"
            },
            headers=headers,
            cookies={"sessionid": request.COOKIES.get("sessionid")},
            timeout=5
        )
        resp.raise_for_status()
        quiz_data = resp.json()
        # print(quiz_data)
        cache.set(f"continue_quiz_{request.user.id}", quiz_data, 60 * 30)
    except Exception as e:
        print("Error fetching unfinished quizzes:", e)
        quiz_data = []

    return render(request, "continue_quiz.html", {"quiz_data": quiz_data})

@session_access_required
def resume_quiz_view(request, session_id):
    quiz_data = {}
    try:
        access_token = request.session.get("access_token")
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        # Call the ResumeQuiz API through the proxy
        resp = requests.get(
            request.build_absolute_uri("/proxy/"),
            params={
                "endpoint": f"/api/quiz/resume/{session_id}/",
                "endpoint_type": "private"
            },
            headers=headers,
            cookies={"sessionid": request.COOKIES.get("sessionid")},
            timeout=5
        )
        resp.raise_for_status()
        quiz_data = resp.json()
        cache.set(f"resume_quiz_{request.user.id}", quiz_data, 60 * 30)
    except Exception as e:
        # print("Error resuming quiz:", e)
        quiz_data = {}

    return render(request, "quiz.html", {"quiz_data": quiz_data})

@session_access_required
def list_retry_quizzes(request):
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    data = get_retryable_quizzes(request, page=page)
    return render(request, "list_retry_quiz.html", data)


@session_access_required
def start_retry(request, score_id):
    quiz_data = cache.get(f"retry_quiz_{score_id}")
    try:
        access_token = request.session.get("access_token")
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        payload = json.dumps({"score_id": score_id})

        resp = requests.post(
            request.build_absolute_uri("/proxy/"),
            params={
                "endpoint": "/api/quiz/start_retry_missed_question/",
                "endpoint_type": "private"
            },
            data=payload,
            headers=headers,
            cookies={"sessionid": request.COOKIES.get("sessionid")},
            timeout=5
        )
        resp.raise_for_status()
        # Add flag to indicate retry quiz
        quiz_data = resp.json()
        quiz_data["is_retry"] = True
        cache.set(f"retry_quiz_{score_id}", quiz_data, 60 * 30)

    except Exception as e:
        # print("Error starting retry:", e)
        quiz_data = []

    return render(request, "quiz.html", {"quiz_data": quiz_data})

@session_access_required
def resume_retry(request, session_id):
    quiz_data = cache.get(f"retry_session_{session_id}")
    try:
        access_token = request.session.get("access_token")
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        # GET request to proxy for the session
        resp = requests.get(
            request.build_absolute_uri("/proxy/"),
            params={
                "endpoint": f"/api/quiz/retry_session/{session_id}/",
                "endpoint_type": "private"
            },
            headers=headers,
            cookies={"sessionid": request.COOKIES.get("sessionid")},
            timeout=5
        )
        resp.raise_for_status()
        quiz_data = resp.json()
        cache.set(f"retry_session_{session_id}", quiz_data, 60 * 30)

    except Exception as e:
        # print("Error resuming retry session:", e)
        quiz_data = []

    return render(request, "quiz.html", {"quiz_data": quiz_data})
