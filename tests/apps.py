from django.apps import AppConfig
from django.db.models.signals import pre_migrate
from django.db import connections

def enable_pg_jsonschema(*_, using, **__):
    connection = connections[using]
    with connection.cursor() as cursor:
        cursor.execute('CREATE EXTENSION IF NOT EXISTS pg_jsonschema;')

class TestsConfig(AppConfig):
    name = "tests"
    verbose_name = "Tests"

    def ready(self):
        pre_migrate.connect(enable_pg_jsonschema)
