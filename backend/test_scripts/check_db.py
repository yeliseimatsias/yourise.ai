# check_db.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourise.settings')
django.setup()

from django.db import connection
from core.models import Session
from laws.models import Catalog

def check_all():
    print("=" * 60)
    print("ПРОВЕРКА ПОДКЛЮЧЕНИЯ DJANGO К БД")
    print("=" * 60)
    
    # 1. Проверка search_path
    with connection.cursor() as cursor:
        cursor.execute("SHOW search_path")
        path = cursor.fetchone()
        print(f"search_path: {path[0]}")
    
    # 2. Проверка видимости таблиц через raw SQL
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM core.sessions")
        count = cursor.fetchone()[0]
        print(f"Через raw SQL: sessions.count = {count}")
    
    # 3. Проверка через ORM
    try:
        session_count = Session.objects.count()
        print(f"Через ORM: sessions.count = {session_count}")
    except Exception as e:
        print(f"ORM ошибка: {e}")
    
    try:
        law_count = Catalog.objects.count()
        print(f"Через ORM: catalog.count = {law_count}")
    except Exception as e:
        print(f"ORM ошибка: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    check_all()