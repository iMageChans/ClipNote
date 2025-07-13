from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'body-parts', views.BodyPartViewSet, basename='bodypart')
router.register(r'exercises', views.ExerciseViewSet, basename='exercise')

urlpatterns = [
    # 路由器的通用模式需要放在前面，这样@action装饰器的路由才能被正确匹配
    path('', include(router.urls)),
    # 更具体的路由模式放在后面作为备用
    path('exercises/<str:body_part_slug>/<str:exercise_slug>/', views.ExerciseViewSet.as_view({'get': 'retrieve'}), name='exercise-detail-legacy'),
    path('exercises/body-parts/<str:body_part_slug>/', views.ExerciseViewSet.as_view({'get': 'by_body_part'}), name='exercise-by-body-part-legacy'),
] 