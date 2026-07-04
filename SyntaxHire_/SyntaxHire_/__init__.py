from .celery import app as celery_app

# Django başladığında bu asenkron yapının da hazır olmasını garanti ediyoruz
__all__ = ('celery_app',)