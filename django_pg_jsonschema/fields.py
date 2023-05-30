import json

from django import forms
from django.core import checks, exceptions
from django.db import connections, router
from django.db.models import JSONField, expressions
from django.utils.translation import gettext_lazy as _
from jsonschema import Validator
from jsonschema.validators import validator_for

__all__ = ["JSONSchemaField"]

PG_JSONSCHEMA_LOOKUP = """
    SELECT EXISTS(
        SELECT 1
        FROM pg_available_extensions
        WHERE name = 'pg_jsonschema'
        AND installed_version IS NOT NULL
    );
"""


class JSONSchemaField(JSONField):
    description = _("A JSON object with JSON Schema")
    default_error_messages = {
        "invalid": _("Value must be valid JSON."),
        "invalid_schema": _("Schema must be valid JSON Schema"),
    }

    # JSON Field can not be empty
    empty_strings_allowed = False

    # By default, we just store an empty dictionary
    _default_hint = ("dict", "{}")

    # Database validation, if this is False, we validate
    # the schema in python instead of the database level
    database_validation = True
    schema = None

    def __init__(self, schema=None, *args, **kwargs):
        if not schema:
            raise TypeError("Schema was not passed to JSONSchemaField")

        # Check if the given schema is valid, if so,
        # we set the schema to the given schema.
        _validator: Validator = validator_for(schema)
        _validator.check_schema(schema)
        self.schema = schema

        # Pass everything up to the JSONField
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.schema:
            kwargs["schema"] = self.schema
        return name, path, args, kwargs


    def get_internal_type(self):
        # Default Django DB type is JSONField, and
        # the check-function handles if we support
        # the database backend. If necessary, it is
        # possible to override the db_type function.
        return "JSONField"

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        databases = kwargs.get("databases") or []
        for db in databases:
            errors.extend(self._check_json_supported(db))
            if self.database_validation:
                errors.extend(self._check_jsonschema_supported(db))

        return errors

    def _check_json_supported(self, db):
        # Check if the model needs migration for this database
        if not router.allow_migrate_model(db, self.model):
            return []

        # Get the current connection for the migration
        connection = connections[db]

        # Check if the connection backend supports JSON
        if not (connection.features.supports_json_field):
            return [
                checks.Error(
                    "%s does not support JSONFields." % connection.display_name,
                    obj=self.model,
                    id="fields.E180",
                )
            ]

    def _check_jsonschema_supported(self, db):
        # Check if the model needs migration for this database
        if not router.allow_migrate_model(db, self.model):
            return []

        # Get the current connection for the migration
        connection = connections[db]

        # Only PostgreSQL is currently supported for JSONSchema
        if not (connection.vendor.lower() == "postgresql"):
            return [
                checks.Error(
                    "Database is not PostgreSQL",
                    obj=self.model,
                    id="django_pg_jsonschema.NOT_PG",
                )
            ]

        # Check if the connection backend supports JSONSchema
        if result := connection.cursor().execute(PG_JSONSCHEMA_LOOKUP):
            print(result)
            return []

        return []

    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "form_class": forms.JSONField,
                **kwargs,
            }
        )

    def get_prep_value(self, value):
        return super().get_prep_value(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        # Keep up to spec with the Django Field definitions
        value = super().get_db_prep_value(value, connection, prepared)
        if not prepared:
            value = self.get_prep_value(value)

        # If the passed value is part of a value expression (Django)
        # we'll need to unpack it first.
        if isinstance(value, expressions.Value) and isinstance(
            value.output_field, JSONSchemaField
        ):
            value = value.value
        # If the raw SQL is given, push that to the database.
        elif hasattr(value, "as_sql"):
            return value

        # Use native functionality for Django 4.2
        if hasattr(connection.ops, "adapt_json_value"):
            return connection.ops.adapt_json_value(value)

        return json.dumps(value)

    def validate(self, value, model_instance):
        #
        #
        #

        super().validate(value, model_instance)
        try:
            json.dumps(value, cls=self.encoder)
        except TypeError:
            raise exceptions.ValidationError(
                self.error_messages["invalid"],
                code="invalid",
                params={"value": value},
            )
