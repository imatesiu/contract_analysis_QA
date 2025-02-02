# Generated by Django 4.1 on 2023-04-11 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0010_remove_doc_doc_text_remove_doc_txt_file_docx_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="NER",
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
                ("txt_file", models.FileField(blank=True, upload_to="")),
                ("jsonDict", models.FileField(blank=True, upload_to="")),
                ("jsonNER", models.FileField(blank=True, upload_to="")),
                ("my_dict", models.JSONField(blank=True, null=True)),
                ("dict_NER", models.JSONField(blank=True, null=True)),
                ("language", models.CharField(max_length=50)),
            ],
        ),
    ]
