from rest_framework import viewsets
from .models import Article
from .serializers import ArticleListSerializer, ArticleDetailSerializer
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
import os
import uuid
from datetime import datetime

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-created_at')
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleDetailSerializer
    
    http_method_names = ['get']

class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        images = request.FILES.getlist('images')
        if not images:
            return Response({"error": "没有上传图片"}, status=status.HTTP_400_BAD_REQUEST)
        
        image_urls = []
        for image in images:
            # 生成唯一文件名
            ext = os.path.splitext(image.name)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            
            # 按年月创建目录
            today = datetime.today()
            relative_path = f"uploads/{today.year}/{today.month:02d}/"
            absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            
            # 确保目录存在
            os.makedirs(absolute_path, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(absolute_path, filename)
            with open(file_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            
            # 生成URL
            image_url = f"{settings.MEDIA_URL}{relative_path}{filename}"
            image_urls.append(image_url)
        
        return Response({"urls": image_urls}, status=status.HTTP_201_CREATED)

# Create your views here.
