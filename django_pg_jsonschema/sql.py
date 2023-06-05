PG_JSONSCHEMA_LOOKUP = """
    SELECT default_version, installed_version
    FROM pg_available_extensions
    WHERE name = 'pg_jsonschema'
    AND installed_version IS NOT NULL;
"""

PG_JSONSCHEMA_CONSTRAINT = """
    BEGIN;

    ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {column}_check;
    ALTER TABLE {table} ADD CONSTRAINT {column}_check
    CHECK (
        jsonb_matches_schema(
            '{schema}',
            {column}
        )
    );

    COMMIT;
"""
