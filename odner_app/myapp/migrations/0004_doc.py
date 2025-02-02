# Generated by Django 4.1 on 2023-03-14 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0003_pdf_pdf_text_alter_pdf_title"),
    ]

    operations = [
        migrations.CreateModel(
            name="DOC",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("doc_file", models.FileField(upload_to="docs/")),
                ("doc_text", models.TextField(blank=True, null=True)),
            ],
        ),
    ]
