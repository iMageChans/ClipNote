from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/admin/', admin.site.urls),  # 保持原来的admin路径
    path('', include('note.urls')),  # note应用的URL
    path('fitness/', include('fitness.urls')),  # fitness应用的URL
]

# 开发环境下提供媒体文件和静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # 生产环境下仍然需要提供媒体文件服务（通常由nginx处理，但作为备用）
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
