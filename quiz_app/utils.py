import math
import requests
from django.urls import reverse

def get_quizzes(request, category_id=None, page=1, search=""):
    access_token = request.session.get('access_token')
    headers = {}
    quizzes = []
    quiz_count = 0
    next_url = None
    prev_url = None

    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    endpoint = "/api/quiz/get_accessible_quizzes/"

    params = {
        "endpoint": endpoint,
        "endpoint_type": "private",
        "page": page,
    }
    if category_id:
        params["category_id"] = category_id
    if search:
        params["search"] = search

    try:
        resp = requests.get(
            request.build_absolute_uri(reverse("proxy_handler")),
            params=params,
            headers=headers,
            cookies={"sessionid": request.COOKIES.get("sessionid")},
            timeout=5
        )
        resp.raise_for_status()
        resp_data = resp.json()

        quizzes = resp_data.get("results", [])
        quiz_count = resp_data.get("count", 0)
        next_url = resp_data.get("next")
        prev_url = resp_data.get("previous")

        # pagination
        has_prev = bool(prev_url)
        has_next = bool(next_url)
        per_page = len(quizzes) or 1
        total_pages = math.ceil(quiz_count / per_page)

        if has_prev and has_next:
            page_numbers = [page - 1, page, page + 1]
        elif has_prev and not has_next:
            start = max(1, page - 2)
            page_numbers = [p for p in [start, start + 1, start + 2] if p <= page]
        elif not has_prev and has_next:
            page_numbers = [page, page + 1, page + 2]
        else:
            page_numbers = [page]

        page_numbers = [p for p in page_numbers if p <= total_pages]
        show_ellipsis = bool(page_numbers) and total_pages > page_numbers[-1]

    except Exception as e:
        # print("Error fetching quizzes:", e)
        quizzes, quiz_count = [], 0
        has_prev = has_next = show_ellipsis = False
        page_numbers = []

    return {
        "quizzes": quizzes,
        "quiz_count": quiz_count,
        "next": next_url,
        "previous": prev_url,
        "page": page,
        "has_prev": has_prev,
        "has_next": has_next,
        "page_numbers": page_numbers,
        "show_ellipsis": show_ellipsis,
        "total_pages": total_pages if quiz_count else 1,
    }

def get_retryable_quizzes(request, page=1):
    access_token = request.session.get("access_token")
    headers = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}" 

    params = {
        "endpoint": "/api/quiz/get_retryable_scores/",
        "endpoint_type": "private",
        "page": page,
    }

    try:
        resp = requests.get(
            request.build_absolute_uri(reverse("proxy_handler")),
            params=params,
            headers=headers,
            cookies={"sessionid": request.COOKIES.get("sessionid")},
            timeout=5
        )
        resp.raise_for_status()
        resp_data = resp.json()
        options = resp_data.get("options", [])
        for option in options:
            option["label"] = f"{option['quiz_name']} ({option['missed_count']} missed)"

        quiz_count = resp_data.get("count", 0)
        next_url = resp_data.get("next")
        prev_url = resp_data.get("previous")

        # pagination
        has_prev = bool(prev_url)
        has_next = bool(next_url)
        per_page = len(options) or 1
        total_pages = math.ceil(quiz_count / per_page)

        if has_prev and has_next:
            page_numbers = [page - 1, page, page + 1]
        elif has_prev and not has_next:
            start = max(1, page - 2)
            page_numbers = [p for p in [start, start + 1, start + 2] if p <= page]
        elif not has_prev and has_next:
            page_numbers = [page, page + 1, page + 2]
        else:
            page_numbers = [page]

        page_numbers = [p for p in page_numbers if p <= total_pages]
        show_ellipsis = bool(page_numbers) and total_pages > page_numbers[-1]

        return {
            "message": resp_data.get("message", ""),
            "options": options,
            "quiz_count": quiz_count,
            "next": next_url,
            "previous": prev_url,
            "page": page,
            "has_prev": has_prev,
            "has_next": has_next,
            "page_numbers": page_numbers,
            "show_ellipsis": show_ellipsis,
            "total_pages": total_pages if quiz_count else 1,
        }

    except Exception as e:
        # print("Error fetching retryable quizzes:", e)
        return {
            "message": "Error fetching quizzes.",
            "options": [],
            "quiz_count": 0,
            "next": None,
            "previous": None,
            "page": 1,
            "has_prev": False,
            "has_next": False,
            "page_numbers": [],
            "show_ellipsis": False,
            "total_pages": 1,
        }
