./manage.py makemigrations api users
./manage.py migrate --run-syncdb
./manage.py collectstatic
./manage.py shell -c "from users.models import User; User.objects.create_superuser('admin', 'admin@tut.by', 'adminpass')"
./manage.py shell -c "from api.models import Tag; Tag.objects.create(name='Hot', color='#ff0000', slug='hot')"
./manage.py shell -c "from api.models import Tag; Tag.objects.create(name='Ice', color='#0000ff', slug='ice')"
./manage.py loaddata ingredients_data.json