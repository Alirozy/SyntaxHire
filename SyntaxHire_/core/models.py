import uuid
from django.db import models

class TimeStampedModel(models.Model):
    """
    This abstract base class provides self-updating 'created_at' and 'updated_at' fields to any model that inherits from it.
    This is useful for tracking when records are created and last modified.
    """
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Updated At"
    )

    class Meta:
        abstract = True  # Bu satır veritabanında tablo oluşmasını engeller.


class UUIDModel(models.Model):
    """
    This abstract base class provides a UUID primary key to any model that inherits from it.
    This is useful for preventing ID prediction and providing a more secure API structure.
    This is optional but recommended for professional projects.
    """
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    class Meta:
        abstract = True