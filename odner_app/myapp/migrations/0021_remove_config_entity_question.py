# Generated by Django 4.1 on 2023-04-22 12:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0020_ner_entity_model_current"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="config",
            name="entity_question",
        ),
    ]
