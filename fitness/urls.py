from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'body-parts', views.BodyPartViewSet, basename='bodypart')
router.register(r'exercises', views.ExerciseViewSet, basename='exercise')

urlpatterns = [
    path('', include(router.urls)),
    # 兼容旧的URL结构
    path('exercises/<str:body_part_slug>/', views.ExerciseViewSet.as_view({'get': 'by_body_part'}), name='exercise-by-body-part-legacy'),
    path('exercises/<str:body_part_slug>/<str:exercise_slug>/', views.ExerciseViewSet.as_view({'get': 'retrieve'}), name='exercise-detail-legacy'),
] 