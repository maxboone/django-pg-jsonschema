from django.db.models import Model
from django_pg_jsonschema.fields import JSONSchemaField

class JSONSchemaFieldModel(Model):
    data = JSONSchemaField(default=dict)
