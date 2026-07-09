from django.shortcuts import render
from .models import Skill
from .serializers import SkillSerializer
from rest_framework import permissions, generics


# Create your views here.
class SkillListView(generics.ListAPIView):
    """
    Sistemdeki tüm teknolojileri listeler (Frontend seçici/dropdown listeleri için).
    Herkese açıktır veya IsAuthenticated yapılabilir.
    """
    queryset = Skill.objects.all().order_by('category', 'name')
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]
