from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'body-parts', views.BodyPartViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('exercises/', views.ExerciseViewSet.as_view({'get': 'list'}), name='exercise-list'),
    path('exercises/search/', views.ExerciseViewSet.as_view({'get': 'list'}), name='exercise-search'),
    path('exercises/<str:body_part_slug>/', views.ExerciseViewSet.as_view({'get': 'by_body_part'}), name='exercise-by-body-part'),
    path('exercises/<str:body_part_slug>/<str:exercise_slug>/', views.ExerciseViewSet.as_view({'get': 'retrieve'}), name='exercise-detail'),
] 