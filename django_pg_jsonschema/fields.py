import json


from django_pg_jsonschema.sql import PG_JSONSCHEMA_LOOKUP
from django_pg_jsonschema.configuration import PG_COMMIT_JSONSCHEMA

from django import forms
from django.db import connections, router
from django.db.models import JSONField, expressions
from django.utils.translation import gettext_lazy as _
from django.core import checks, exceptions

from jsonschema import Validator
from jsonschema.validators import validator_for

__all__ = ["JSONSchemaField"]


class JSONSchemaField(JSONField):
    description = _("A JSON object with JSON Schema")
    default_error_messages = {
        "invalid": _("Value must be valid JSON."),
        "invalid_schema": _("Schema must be valid JSON Schema"),
        "invalid_object": _("Object does not adhere to JSON Schema")
    }

    # JSON Field can not be empty
    empty_strings_allowed = False

    # By default, we just store an empty dictionary
    _default_hint = ("dict", "{}")

    # Database validation, if this is False, we validate
    # the schema in python instead of the database level
    check_schema_in_db = PG_COMMIT_JSONSCHEMA

    validator = None
    validator_schema = None

    def __init__(self, schema=None, check_schema_in_db=True, *args, **kwargs):
        if not schema:
            raise TypeError("Schema was not passed to JSONSchemaField")

        if not isinstance(check_schema_in_db, bool):
            raise TypeError("Given check_schema_in_db argument is not a boolean")

        # Set flag to commit the check to DB on migrations
        self.check_schema_in_db = check_schema_in_db

        # Create a validator object using the JSONSchema
        self.validator = self.create_validator(schema)
        self.validator_schema = schema

        # Pass everything up to the JSONField
        super().__init__(*args, **kwargs)

    def create_validator(self, schema) -> Validator:
        # Check if the given schema is valid, if so,
        # we set the schema to the given schema.
        validator: Validator = validator_for(schema)
        validator.check_schema(schema)
        return validator

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["check_schema_in_db"] = self.check_schema_in_db
        if self.validator and self.validator_schema:
            kwargs["schema"] = self.validator_schema
        return name, path, args, kwargs

    def check(self, **kwargs):
        errors = super().check(**kwargs)

        databases = kwargs.get("databases") or []
        for db in databases:
            if self.check_schema_in_db:
                errors.extend(self._check_jsonschema_supported(db))

        return errors

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
        # probably best to spilt this off to a different file
        # in the future.
        if self.check_schema_in_db:
            cursor = connection.cursor()
            cursor.execute(PG_JSONSCHEMA_LOOKUP)
            result = cursor.fetchone()

            # There's a result, so it's installed
            if result and len(result) == 2:
                if result[1]:
                    return []

                return [
                    checks.Warning(
                        f"pg_jsonschema { result[0] } installed in DB but not enabled",
                        obj=self.model,
                        id="django_pg_jsonschema.PG_JSONSCHEMA_NOT_ENABLED"
                    )
                ]

            return [
                checks.Warning(
                    "pg_jsonschema not installed in DB",
                    obj=self.model,
                    id="django_pg_jsonschema.PG_JSONSCHEMA_NOT_FOUND"
                )
            ]

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

        # adapt_json_value added in Django 4.1, add this
        # conditional for compat with older versions
        if hasattr(connection.ops, "adapt_json_value"):
            return connection.ops.adapt_json_value(value)

        return json.dumps(value)

    def validate(self, value, model_instance):
        try:
            self.validator.validate(value)
        except TypeError:
            raise exceptions.ValidationError(
                self.error_messages["invalid_object"],
                code="invalid_object",
                params={"value": value}
            )

        super().validate(value, model_instance)
