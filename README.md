# Django PostgreSQL JSONSchema

Django PostgreSQL JSONSchema is a package that provides an extension to
Django's PostgreSQL JSONField, by adding support and functions for PostgreSQL
installations with [`pg_jsonschema`](https://github.com/supabase/pg_jsonschema).

This allows developers to store data in a JSONField, while running validation
over the field and having the ability to generate forms for these model fields.

## Features

- **Custom JSON Field**: Extends Django's built-in `JSONField` to support JSON Schema validation.
- **PostgreSQL JSONSchema**: Choose whether you want to validate the data in Python or commit the JSONSchema to the DB.
- **Querying Support**: Utilize Django's ORM capabilities to query and filter data stored in the JSON field.
- **Schema Migration**: Perform schema migrations smoothly without data loss or compatibility issues.

## Installation

You can install the package using pip:

```shell
pip install django-pg-jsonschema
```

## Usage

1. Add `'django_pg_jsonschema'` to your Django project's `INSTALLED_APPS` in the settings module.

2. Configure globally if you want to commit the schemas to PostgreSQL (in `settings.py`):

    ```python
    DJANGO_PG_JSONSCHEMA = {
        'PG_COMMIT_JSONSCHEMA': True
    }
    ```

3. Import the `JSONSchemaField` from the package:

    ```python
    from django_pg_jsonschema.fields import JSONSchemaField
    ```

4. In your Django model, define a field of type `JSONSchemaField` argument specifying the JSON schema:

   ```python
   class Person(models.Model):
        data = JSONSchemaField(schema={
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0},
            },
            "required": ["name", "age"]
        })
   ```

   In the above example, the `data` field will store JSON objects that adhere to the specified schema.

5. Optionally, you can define whether you want the check to be added as a constraint to the database:

   ```python
   class Person(models.Model):
        data = JSONSchemaField(
            schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer", "minimum": 0},
                },
                "required": ["name", "age"]
            },
            check_schema_in_db=False
        )
   ```

6. Use the field in your Django models as you would with any other field:

   ```python
   obj = Person(data={"name": "John Doe", "age": 25})
   obj.save()
   ```

## Contribution

Contributions to the Django JSON Field with JSON Schema Support package are welcome! If you encounter any issues, have suggestions, or want to contribute code, please open an issue

 or submit a pull request on the GitHub repository: [https://github.com/maxboone/django-pg-jsonschema](https://github.com/maxboone/django-pg-jsonschema)

Please make sure to follow the [contribution guidelines](CONTRIBUTING.md) before submitting your contributions.

## License

This package is licensed under the [Apache 2.0 License](LICENSE).
