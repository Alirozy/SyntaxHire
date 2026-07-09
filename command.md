docker compose exec -it web sh
python manage.py makemigrations
python manage.py migrate
python manage.py startapp

cd SyntaxHire_

# 1. Tüm container'ları ve veritabanı volume'unu tamamen silerek durdur
docker compose down -v

# 2. Container'ları arka planda yeniden ayağa kaldır
docker compose up -d

# 3. Şimdi temiz veritabanına migrate komutunu gönder
docker compose exec web python manage.py migrate