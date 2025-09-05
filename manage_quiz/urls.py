from django.urls import path
from .views import add_quiz, manage_quiz, instruction

app_name = 'manage_quiz'
urlpatterns = [
    path('add_quiz/', add_quiz, name='add_quiz'),
    path('manage_quiz/', manage_quiz, name='manage_quiz'),
    path('instruction/', instruction, name='instruction'),
]
