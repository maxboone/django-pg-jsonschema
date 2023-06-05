from django.db.models import Model
from django_pg_jsonschema.fields import JSONSchemaField


class JSONSchemaFieldModel(Model):
    data = JSONSchemaField(
        default=dict,
        schema={
            "type": "object",
            "properties": {"name": {"type": "string"}, "optional": {"type": "number"}},
            "required": ["name"],
        },
    )
