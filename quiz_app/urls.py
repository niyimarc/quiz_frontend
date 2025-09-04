from django.urls import path
from .views import list_quiz, start_quiz, continue_quiz_view, list_retry_quizzes, resume_quiz_view, start_retry, resume_retry

app_name = 'quiz_app'
urlpatterns = [
    path('', list_quiz, name='list_quiz'),
    path('quiz/<int:quiz_id>/', start_quiz, name='start_quiz'),
    path('continue_quiz', continue_quiz_view, name='continue_quiz'),
    path('resume_quiz/<int:session_id>/', resume_quiz_view, name='resume_quiz'),
    path('quiz/retryable/', list_retry_quizzes, name='list_retry_quizzes'),
    path('quiz/start_retry/<int:score_id>/', start_retry, name='start_retry'),
    path('quiz/resume_retry/<int:retry_session_id>/', resume_retry, name='resume_retry'),
]
