from django.apps import AppConfig
from django.db.models.signals import post_migrate

from django_pg_jsonschema.signals import migrate_signal
from django_pg_jsonschema.configuration import PG_COMMIT_JSONSCHEMA


class DjangpPgJsonschema(AppConfig):
    name = "django_pg_jsonschema"
    verbose_name = "Django PostgreSQL JSONSchema"

    def ready(self):
        if (PG_COMMIT_JSONSCHEMA):
            post_migrate.connect(migrate_signal)
