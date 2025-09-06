from .base import *

DEBUG = False
ALLOWED_HOSTS = ["www.quiz.speedspro.us", "quiz.speedspro.us"]

# this is the path to the static folder where css, js and images are stored
STATIC_DIR = BASE_DIR / '/home/speebndt/quiz_frontend/static/'

STATIC_URL = 'static/'
STATIC_ROOT = '/home/speebndt/quiz.speedspro.us/static/'

STATICFILES_DIRS = [
    STATIC_DIR,
]