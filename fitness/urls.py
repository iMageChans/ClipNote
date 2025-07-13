from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'body-parts', views.BodyPartViewSet, basename='bodypart')
router.register(r'exercises', views.ExerciseViewSet, basename='exercise')

urlpatterns = [
    # DRF路由器处理所有路由
    path('', include(router.urls)),
] 