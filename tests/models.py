from django.db.models import Model
from django_pg_jsonschema.fields import JSONSchemaField


class SingleDBModel(Model):
    data = JSONSchemaField(
        default=dict,
        schema={
            "type": "object",
            "properties": {"name": {"type": "string"}, "optional": {"type": "number"}},
            "required": ["name"],
        },
        check_schema_in_db=True
    )

class SinglePythonModel(Model):
    data = JSONSchemaField(
        default=dict,
        schema={
            "type": "object",
            "properties": {"name": {"type": "string"}, "optional": {"type": "number"}},
            "required": ["name"],
        },
        check_schema_in_db=False
    )
