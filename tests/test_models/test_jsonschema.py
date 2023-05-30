from django.test import TestCase
from tests.models import JSONSchemaFieldModel

class JSONSchemaFieldTests(TestCase):
    def setUp(self):
        self.model = JSONSchemaFieldModel.objects.create()

    def test_true(self):
        self.assertEqual(1, 1)
