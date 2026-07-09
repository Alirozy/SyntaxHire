import uuid
from django.db import models
from core.models import  TimeStampedModel

# Create your models here.


class Skill(TimeStampedModel):
    """
    Sistemdeki tüm teknolojilerin (Go, Python, Docker vb.) tutulduğu ana tablo.
    Arama, filtreleme ve yetenek eşleştirme algoritmaları için kritik öneme sahiptir.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="Skill Name")
    category = models.CharField(max_length=100, blank=True, null=True, db_index=True, verbose_name="Category (e.g., Backend)")

    def __str__(self):
        return self.name
    
    