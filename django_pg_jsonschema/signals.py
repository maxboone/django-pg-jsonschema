from django.db.models import Model
from django.db import connections
from django_pg_jsonschema.fields import JSONSchemaField
from django_pg_jsonschema.sql import PG_JSONSCHEMA_CONSTRAINT
from django.db.migrations.state import StateApps
import json


def has_jsonschemafield(model: Model):
    return any(isinstance(i, JSONSchemaField) for i in model._meta.fields)


def ensure_model_constraints(model: Model, using: str = "default"):
    connection = connections[using]
    schemas: dict[str, dict] = {}

    for field in model._meta.fields:
        if isinstance(field, JSONSchemaField):
            if field.check_schema_in_db:
                schemas[field.db_column or field.name] = field.validator_schema

    for column, schema in schemas.items():
        with connection.cursor() as cursor:
            cursor.execute(
                PG_JSONSCHEMA_CONSTRAINT.format(
                    table=model._meta.db_table,
                    column=column,
                    schema=json.dumps(schema),
                )
            )


def migrate_signal(*_, apps: StateApps, using: str, **__):
    # Get the historical models from the migration state
    all_models = apps.all_models

    for _, models in all_models.items():
        for _, model in models.items():
            if has_jsonschemafield(model):
                ensure_model_constraints(model, using=using)
