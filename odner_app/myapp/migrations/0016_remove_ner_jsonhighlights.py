# Generated by Django 4.1 on 2023-04-13 14:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0015_ner_jsonhighlights"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ner",
            name="jsonHighlights",
        ),
    ]
