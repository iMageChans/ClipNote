from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import BodyPart, Exercise
from .serializers import BodyPartSerializer, ExerciseListSerializer, ExerciseDetailSerializer


class StandardResultsSetPagination(PageNumberPagination):
    """自定义分页类"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


class BodyPartViewSet(viewsets.ReadOnlyModelViewSet):
    """身体部位ViewSet"""
    queryset = BodyPart.objects.all()
    serializer_class = BodyPartSerializer
    lookup_field = 'slug'
    pagination_class = None  # 身体部位通常不多，不需要分页


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """健身动作ViewSet"""
    queryset = Exercise.objects.all().select_related('body_part')
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'body_part__name']
    ordering_fields = ['name', 'created_at', 'updated_at', 'body_part__name']
    ordering = ['-created_at']  # 默认按创建时间倒序
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'by_body_part' or self.action == 'recommendations':
            return ExerciseListSerializer
        return ExerciseDetailSerializer
    
    def get_queryset(self):
        """优化查询集"""
        queryset = super().get_queryset()
        
        # 如果有body_part参数，添加过滤
        body_part_slug = self.kwargs.get('body_part_slug')
        if body_part_slug:
            queryset = queryset.filter(body_part__slug=body_part_slug)
            
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        获取动作列表，支持搜索、排序和分页
        
        查询参数：
        - search: 搜索关键词（在名称、描述、部位名称中搜索）
        - ordering: 排序字段（name, created_at, updated_at, body_part__name）
        - page: 页码
        - page_size: 每页数量（最大100）
        """
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, pk=None, body_part_slug=None, exercise_slug=None):
        """
        通过主键、部位slug和动作slug获取特定动作详情
        """
        queryset = self.get_queryset()
        
        # 如果有body_part_slug和exercise_slug，使用它们来查找
        if body_part_slug and exercise_slug:
            exercise = get_object_or_404(queryset, 
                                       body_part__slug=body_part_slug, 
                                       slug=exercise_slug)
        else:
            # 否则使用pk查找
            exercise = get_object_or_404(queryset, pk=pk)
        
        serializer = self.get_serializer(exercise)
        return Response(serializer.data)
    
    @action(detail=False, url_path='by-body-part/(?P<body_part_slug>[^/.]+)')
    def by_body_part(self, request, body_part_slug=None):
        """
        获取特定部位的所有动作，支持分页和搜索
        
        查询参数：
        - search: 搜索关键词
        - ordering: 排序字段
        - page: 页码
        - page_size: 每页数量
        """
        # 验证body_part是否存在
        get_object_or_404(BodyPart, slug=body_part_slug)
        
        queryset = self.get_queryset().filter(body_part__slug=body_part_slug)
        
        # 应用搜索过滤
        queryset = self.filter_queryset(queryset)
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, url_path='(?P<body_part_slug>[^/.]+)/recommendations')
    def recommendations(self, request, body_part_slug=None):
        """
        获取特定身体部位的推荐动作（随机8个）
        """
        # 验证body_part是否存在
        get_object_or_404(BodyPart, slug=body_part_slug)
        
        queryset = Exercise.objects.filter(body_part__slug=body_part_slug).select_related('body_part')
        
        # 随机选择8个动作
        recommended_exercises = queryset.order_by('?')[:8]
        
        serializer = self.get_serializer(recommended_exercises, many=True)
        return Response({
            'body_part': body_part_slug,
            'count': len(recommended_exercises),
            'recommendations': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        专门的搜索接口
        
        查询参数：
        - search: 搜索关键词（必需）
        - body_part: 限制在特定身体部位中搜索
        - ordering: 排序字段
        - page: 页码
        - page_size: 每页数量
        """
        search_query = request.query_params.get('search')
        if not search_query:
            return Response({
                'error': '请提供搜索关键词',
                'detail': '使用 ?search=关键词 进行搜索'
            }, status=400)
        
        queryset = self.get_queryset()
        
        # 可选的身体部位过滤
        body_part = request.query_params.get('body_part')
        if body_part:
            queryset = queryset.filter(body_part__slug=body_part)
        
        # 应用搜索和其他过滤器
        queryset = self.filter_queryset(queryset)
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
            # 添加搜索信息
            response_data['search_query'] = search_query
            if body_part:
                response_data['body_part_filter'] = body_part
            return Response(response_data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'search_query': search_query,
            'body_part_filter': body_part,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        获取统计信息
        """
        from django.db.models import Count
        
        total_exercises = Exercise.objects.count()
        exercises_with_youtube = Exercise.objects.exclude(youtube_url='').count()
        ai_generated = Exercise.objects.filter(ai_generated=True).count()
        
        body_part_stats = BodyPart.objects.annotate(
            exercise_count=Count('exercises')
        ).values('name', 'slug', 'exercise_count').order_by('-exercise_count')
        
        return Response({
            'total_exercises': total_exercises,
            'exercises_with_youtube': exercises_with_youtube,
            'exercises_without_youtube': total_exercises - exercises_with_youtube,
            'ai_generated_descriptions': ai_generated,
            'manual_descriptions': total_exercises - ai_generated,
            'body_part_distribution': list(body_part_stats)
        })
