from django.conf import settings

settings_dict = getattr(settings, 'DJANGO_PG_JSONSCHEMA', {})

# If set to true, commit the JSONSchema to the database
PG_COMMIT_JSONSCHEMA = settings_dict.get('PG_COMMIT_JSONSCHEMA', False)

__all__ = [
    'PG_COMMIT_JSONSCHEMA'
]
