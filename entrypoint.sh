#!/bin/sh
set -e

echo "Aguardando banco de dados..."
until python -c "
import os, MySQLdb
try:
    MySQLdb.connect(
        host=os.environ['DB_HOST'],
        port=int(os.environ.get('DB_PORT', 3306)),
        user=os.environ['DB_USER'],
        passwd=os.environ['DB_PASSWORD'],
        db=os.environ['DB_NAME'],
    )
    print('Banco disponivel.')
except Exception as e:
    print(f'Aguardando: {e}')
    exit(1)
"; do
  sleep 2
done

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn sistema_vendas.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120
