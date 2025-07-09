from django.urls import path, include
from .views import ImageUploadView, ArticleViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')

urlpatterns = [
    path('upload-images/', ImageUploadView.as_view(), name='upload-images'),
    path('list/', ArticleViewSet.as_view({'get': 'list_with_urls'}), name='article-list-with-urls'),
    path('', include(router.urls)),
]