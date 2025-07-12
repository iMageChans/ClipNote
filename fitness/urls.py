from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'body-parts', views.BodyPartViewSet, basename='bodypart')
router.register(r'exercises', views.ExerciseViewSet, basename='exercise')

urlpatterns = [
    # 更具体的路由模式需要放在前面
    path('exercises/<str:body_part_slug>/<str:exercise_slug>/', views.ExerciseViewSet.as_view({'get': 'retrieve'}), name='exercise-detail-legacy'),
    path('exercises/<str:body_part_slug>/', views.ExerciseViewSet.as_view({'get': 'by_body_part'}), name='exercise-by-body-part-legacy'),
    # 路由器的通用模式放在最后
    path('', include(router.urls)),
] 