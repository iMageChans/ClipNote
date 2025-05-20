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
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.http import Http404
from django.utils.text import slugify

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all().order_by('-created_at')
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'  # 保留 slug 作为查找字段，但 URL 将使用关键词
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """
        重写 retrieve 方法，支持通过 slug、id 或关键词获取文章详情
        """
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        slug_or_id_or_keyword = kwargs.get(lookup_url_kwarg)
        
        try:
            # 尝试通过 ID 获取文章（如果是数字）
            if slug_or_id_or_keyword.isdigit():
                article = get_object_or_404(Article, id=int(slug_or_id_or_keyword))
            else:
                # 尝试通过 slug 获取文章
                try:
                    article = Article.objects.get(slug=slug_or_id_or_keyword)
                except Article.DoesNotExist:
                    # 尝试通过关键词获取文章
                    found = False
                    articles = Article.objects.all()
                    for art in articles:
                        keywords = art.get_keywords()
                        # 将关键词转换为 URL 友好的格式（用连字符替换空格）
                        url_keywords = [keyword.replace(' ', '-').lower() for keyword in keywords]
                        if slug_or_id_or_keyword.lower() in url_keywords:
                            article = art
                            found = True
                            break
                    
                    if not found:
                        raise Http404("文章不存在")
            
            serializer = self.get_serializer(article)
            return Response(serializer.data)
        except (ValueError, Http404):
            raise Http404("文章不存在")
    
    @action(detail=False, methods=['get'])
    def list_with_urls(self, request):
        """
        返回带有 URL 的文章列表，URL 使用关键词而不是 slug
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # 确保所有文章都有 slug
        for article in queryset:
            if not article.slug:
                # 生成 slug
                base_slug = slugify(article.title)
                slug = base_slug
                counter = 1
                while Article.objects.filter(slug=slug).exclude(id=article.id).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                article.slug = slug
                article.save(update_fields=['slug'])
        
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = ArticleListSerializer(page, many=True, context={'request': request})
            response_data = self.get_paginated_response(serializer.data).data
            
            # 为每篇文章添加 URL，使用关键词而不是 slug
            for item in response_data['results']:
                keywords = item.get('keywords', [])
                if keywords:
                    # 使用第一个关键词作为 URL
                    keyword = keywords[0].replace(' ', '-').lower()
                    item['url'] = f"{settings.SITE_URL}/api/articles/{keyword}"
                elif item.get('slug'):
                    # 如果没有关键词，则使用 slug
                    item['url'] = f"{settings.SITE_URL}/api/articles/{item.get('slug')}"
                else:
                    # 如果没有关键词和 slug，则使用 ID
                    item['url'] = f"{settings.SITE_URL}/api/articles/{item.get('id')}"
            
            return Response(response_data)
        
        serializer = ArticleListSerializer(queryset, many=True, context={'request': request})
        data = serializer.data
        
        # 为每篇文章添加 URL，使用关键词而不是 slug
        for item in data:
            keywords = item.get('keywords', [])
            if keywords:
                # 使用第一个关键词作为 URL
                keyword = keywords[0].replace(' ', '-').lower()
                item['url'] = f"{settings.SITE_URL}/api/articles/{keyword}"
            elif item.get('slug'):
                # 如果没有关键词，则使用 slug
                item['url'] = f"{settings.SITE_URL}/api/articles/{item.get('slug')}"
            else:
                # 如果没有关键词和 slug，则使用 ID
                item['url'] = f"{settings.SITE_URL}/api/articles/{item.get('id')}"
        
        return Response(data)

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
