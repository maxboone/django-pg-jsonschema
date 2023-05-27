from django.db.models import Field
from django.db.models.fields.mixins import CheckFieldDefaultMixin
from django.utils.translation import gettext_lazy as _

class JSONSchemaField(CheckFieldDefaultMixin, Field):
    empty_strings_allowed = False
    description = _("A JSON object with JSON Schema")
    default_error_messages = {
        "invalid": _("Value must be valid JSON."),
    }
    _default_hint = ("dict", "{}")

    def db_type(self, connection):
        return 'json'
