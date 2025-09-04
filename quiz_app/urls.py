from django.urls import path
from .views import list_quiz, start_quiz

app_name = 'quiz_app'
urlpatterns = [
    path('', list_quiz, name='list_quiz'),
    path('quiz/<int:quiz_id>/', start_quiz, name='start_quiz'),
]
