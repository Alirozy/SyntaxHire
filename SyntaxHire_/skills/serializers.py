from rest_framework import serializers
from .models import Skill


class SkillSerializer(serializers.ModelSerializer):
    """Sistemdeki tüm global yeteneklerin listelenmesi için."""
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category']
        read_only_fields = ['id']