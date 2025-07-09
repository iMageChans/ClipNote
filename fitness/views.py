from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import BodyPart, Exercise
from .serializers import BodyPartSerializer, ExerciseListSerializer, ExerciseDetailSerializer

class BodyPartViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BodyPart.objects.all()
    serializer_class = BodyPartSerializer
    lookup_field = 'slug'

class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exercise.objects.all().select_related('body_part')
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExerciseListSerializer
        return ExerciseDetailSerializer
    
    def retrieve(self, request, body_part_slug=None, exercise_slug=None):
        """
        通过部位slug和动作slug获取特定动作
        """
        queryset = self.get_queryset()
        exercise = get_object_or_404(queryset, 
                                   body_part__slug=body_part_slug, 
                                   slug=exercise_slug)
        serializer = self.get_serializer(exercise)
        return Response(serializer.data)
    
    @action(detail=False)
    def by_body_part(self, request, body_part_slug=None):
        """
        获取特定部位的所有动作
        """
        queryset = self.get_queryset().filter(body_part__slug=body_part_slug)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
