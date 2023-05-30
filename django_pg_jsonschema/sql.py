PG_JSONSCHEMA_LOOKUP = """
    SELECT default_version, installed_version
    FROM pg_available_extensions
    WHERE name = 'pg_jsonschema'
    AND installed_version IS NOT NULL;
"""
