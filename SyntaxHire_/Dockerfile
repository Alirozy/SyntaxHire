# Python'ın resmi hafif imajını kullanıyoruz
FROM python:3.12-slim

# Python'ın çıktıları anlık olarak terminale basmasını sağlar
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Çalışma dizinini ayarlıyoruz
WORKDIR /app

# PostgreSQL için gerekli olan sistem bağımlılıklarını kuruyoruz
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları kopyalayıp kuruyoruz
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarının geri kalanını kopyalıyoruz
COPY . /app/

# Django'nun çalışacağı portu belirtiyoruz
EXPOSE 8000

# Projeyi ayağa kaldıracak komut
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]