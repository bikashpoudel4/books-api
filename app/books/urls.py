from email.policy import default
from django.db import router
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from books import views

router = DefaultRouter()
router.register('tags', views.TagViewset)
router.register('genres', views.GenreViewSet)
router.register('books', views.BookViewSet)

app_name = 'books'

urlpatterns = [
     path('', include(router.urls))
]
