# Django PostgreSQL JSONSchema

Django PostgreSQL JSONSchema is a package that provides an extension to
Django's PostgreSQL JSONField, by adding support and functions for PostgreSQL 
installations with [`pg_jsonschema`](https://github.com/supabase/pg_jsonschema).

This allows developers to store data in a JSONField, while running validation
over the field and having the ability to generate forms for these model fields. 

## Features

- **Custom JSON Field**: Replace Django's built-in `JSONField` with a custom field that supports JSON Schema validation.
- **PostgreSQL JSONSchema**: Choose whether you want to validate the data in Django or commit the JSONSchema to the DB.
- **Schema Validation Hooks**: Define pre-save and post-save hooks to perform custom actions when the JSON data passes or fails the schema validation.
- **Querying Support**: Utilize Django's ORM capabilities to query and filter data stored in the JSON field.
- **Schema Migration**: Perform schema migrations smoothly without data loss or compatibility issues.

## Installation

You can install the package using pip:

```shell
pip install django-pg-jsonschema
```

## Usage

1. Add `'pg_jsonschema'` to your Django project's `INSTALLED_APPS` in the settings module.

2. Import the `JSONField` from the package:

   ```python
   from pg_jsonschema.fields import JSONField
   ```

3. In your Django model, define a field of type `JSONField` with an optional `schema` argument specifying the JSON schema:

   ```python
   class Person(models.Model):
       data = JSONField(schema={
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

4. Optionally, you can define pre-save and post-save hooks to perform custom actions when the JSON data passes or fails the schema validation:

   ```python
   class MyModel(models.Model):
       data = JSONField(
           schema={
               "$schema": "http://json-schema.org/draft-07/schema#",
               "type": "object",
               "properties": {
                   "name": {"type": "string"},
                   "age": {"type": "integer", "minimum": 0},
               },
               "required": ["name", "age"]
           },
           on_valid=lambda instance, data: instance.update_name_length(),
           on_invalid=lambda instance, data: instance.log_validation_error()
       )

       def update_name_length(self):
           self.data['name_length'] = len(self.data['name'])

       def log_validation_error(self):
           logger.error('Invalid JSON data: %s', self.data)
   ```

   In the above example, the `update_name_length()` method will be called before saving the model instance if the JSON data passes the schema validation. Similarly, the `log_validation_error()` method will be called if the JSON data fails the schema validation.

5. Use the field in your Django models as you would with any other field:

   ```python
   obj = Person(data={"name": "John Doe", "age": 25})
   obj.save()
   ```

## Contribution

Contributions to the Django JSON Field with JSON Schema Support package are welcome! If you encounter any issues, have suggestions, or want to contribute code, please open an issue

 or submit a pull request on the GitHub repository: [https://github.com/maxboone/django-pg-jsonschema](https://github.com/maxboone/django-pg-jsonschema)

Please make sure to follow the [contribution guidelines](CONTRIBUTING.md) before submitting your contributions.

## License

This package is licensed under the [MIT License](LICENSE). Feel free to use it in your own projects or modify it to suit your needs.