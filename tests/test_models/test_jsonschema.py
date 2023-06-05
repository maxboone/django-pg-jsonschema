from django.test import TestCase
from django.db import IntegrityError
from jsonschema.exceptions import ValidationError
from tests.models import SingleDBModel, SinglePythonModel
from pytest import raises


class JSONSchemaFieldDBTests(TestCase):
    def test_object_required(self):
        SingleDBModel.objects.create(data={"name": "hello"})

    def test_object_optional(self):
        SingleDBModel.objects.create(data={"name": "hello", "optional": 1})

    def test_object_missing(self):
        with raises(IntegrityError):
            SingleDBModel.objects.create(data={})

    def test_object_mistyped(self):
        with raises(IntegrityError):
            SingleDBModel.objects.create(data={
                "name": "hello",
                "optional": "string"
            })

class JSONSchemaFieldPythonTests(TestCase):
    def test_object_required(self):
        SinglePythonModel.objects.create(data={"name": "hello"})

    def test_object_optional(self):
        SinglePythonModel.objects.create(data={"name": "hello", "optional": 1})

    def test_object_missing(self):
        with raises(ValidationError):
            SinglePythonModel.objects.create(data={})

    def test_object_mistyped(self):
        with raises(ValidationError):
            SinglePythonModel.objects.create(data={
                "name": "hello",
                "optional": "string"
            })
