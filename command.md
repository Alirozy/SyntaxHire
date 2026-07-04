docker compose exec -it web sh
python manage.py makemigrations
python manage.py migrate
python manage.py startapp