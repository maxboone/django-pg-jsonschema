from django.db.models import Model
from django_pg_jsonschema.fields import JSONSchemaField

class JSONSchemaFieldTest(Model):
    data = JSONSchemaField()
