import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_pr.settings')

# Call django.setup() to load the settings module
django.setup()

# Get all the models in your Django app
from django.apps import apps
app_models = apps.get_app_config('myapp').get_models()

# Loop through all the models and delete all the records
for model in app_models:
    model.objects.all().delete()
