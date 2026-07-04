import os
from celery import Celery

# Django'nun ayar dosyasını Celery'ye tanıtıyoruz
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SyntaxHire_.settings') # 'core' yerine kendi ana proje klasörünün adı gelmeli

app = Celery('SyntaxHire_') # Projene verdiğin herhangi bir isim

# Settings.py içindeki "CELERY_" ile başlayan tüm ayarları otomatik yükle deriz
app.config_from_object('django.conf:settings', namespace='CELERY')

# Uygulamalarının (apps) içindeki tasks.py dosyalarını otomatik olarak tarar ve bulur
app.autodiscover_tasks()