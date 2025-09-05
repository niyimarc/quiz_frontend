import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import get_my_quizzes
from auth_app.utils import session_access_required

@session_access_required
def add_quiz(request):
    if request.method == "POST":
        # Get form values
        name = request.POST.get("name")
        sheet_url = request.POST.get("sheet_url")
        status = request.POST.get("status", "public").lower()

        # Make category_ids a list (even if user selects one category)
        category_id = request.POST.get("category")
        category_ids = [category_id] if category_id else []

        # Prepare payload as dict with proper list handling
        payload = {
            "name": name,
            "sheet_url": sheet_url,
            "status": status,
            "category_ids": category_ids  # send as list
        }

        print("Payload for proxy:", payload)

        # Headers
        headers = {"Content-Type": "application/json"}
        access_token = request.session.get("access_token")
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        try:
            resp = requests.post(
            request.build_absolute_uri("/proxy/"),
            params={"endpoint": "/api/quiz/add_quiz/", "endpoint_type": "private"},
            json=payload,  # <-- use json=payload instead of data=payload
            headers=headers,
            cookies={"sessionid": request.COOKIES.get("sessionid")},
            timeout=10
        )

            result = resp.json()
            if resp.status_code == 200:
                messages.success(request, result.get("message", "Quiz added successfully!"))
            else:
                messages.error(request, result.get("error", "Failed to add quiz."))
        except requests.RequestException as e:
            print("Error adding quiz:", e)
            messages.error(request, "Failed to add quiz. Please try again.")


    return render(request, "add_quiz.html")

@session_access_required
def manage_quiz(request):
    request.skip_quiz_categories_context = False
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    category_id = request.GET.get("category_id")
    search = request.GET.get("search", "")
    data = get_my_quizzes(request, category_id=category_id, page=page, search=search)
    return render(request, "manage_quiz.html", data)

def instruction(request):
    return render(request, "instruction.html")