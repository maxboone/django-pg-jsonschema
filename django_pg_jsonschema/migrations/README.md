# Django PG JSONSchema - Migrations

The Django autodetection / state / migration system does
not support custom fields to add operations to a migration
(say AddField, RemoveField, AlterField) with complex logic.

Thus, we can not add a hook to a field that keeps track of
the JSONSchemas in the database. Because we can do validation
in Python, it's currently sufficient to this through the field.

However, the goal of this library is to commit the schemas to
database so we can better ensure the validity of the fields.

There are three ways to go about this:

### 1. Write a new management command

We provide alternative commands to `makemigrations` and `migrate`
which call the respective migration commands, but also keep track
of the JSONSchemas in these migrations. This is similar to patching,
but rather specified elsewhere.

Problem, this changes the general behaviour and command usage,
creating friction in adaptation of this library.

### 2. Patch the migration context

We patch the current Django AutoDetector, Migration & ModelState,
adding in the code to keep track of whatever is going on with our
fields.

Problem, this patches expected behaviour, can cloud bug detection
and will conflict with another library that patches the
migrations.

### 3. Use signals (somehow)

Don't keep track of the JSONField state, but rather use Django signals
to receive saved fields & models, see if there was any change to a
JSONSchemaField and correct the registered JSONSchemaFields.

Problem, this does not store the historic JSONSchemas in the migrations
and does not support easy rollbacks. It does not use the state defined
in the migrations table, but rather the current code state.
