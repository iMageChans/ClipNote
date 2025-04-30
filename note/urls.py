from django.urls import path
from .views import ImageUploadView
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')

urlpatterns = [
    path('upload-images/', ImageUploadView.as_view(), name='upload-images'),
]

urlpatterns += router.urls