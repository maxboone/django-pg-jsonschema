from django import forms
from django.core import checks
from django.db import connections, router
from django.db.models import Field
from django.db.models.fields.mixins import CheckFieldDefaultMixin
from django.utils.translation import gettext_lazy as _

__all__ = [
    "JSONSchemaField"
]

PG_JSONSCHEMA_LOOKUP = '''
    SELECT EXISTS(
        SELECT 1
        FROM pg_available_extensions
        WHERE name = 'pg_jsonschema'
        AND installed_version IS NOT NULL
    );
'''

class JSONSchemaField(CheckFieldDefaultMixin, Field):
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
        if not (connection.vendor.lower() == 'postgresql'):
            return [
                checks.Error(
                    "Database is not PostgreSQL",
                    obj=self.model,
                    id="django_pg_jsonschema.NOT_PG"
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
