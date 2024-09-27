import logging
import os
from django.db import migrations
from django.contrib.auth import get_user_model
logger = logging.getLogger(__name__)



class Migration(migrations.Migration):

    def generate_superuser(apps, schema_editor):
        USERNAME = os.environ.get("ADMIN_USERNAME", 'admin')
        PASSWORD = os.environ.get("ADMIN_PASSWORD", 'adminadmin')
        EMAIL = os.environ.get("ADMIN_EMAIL", '')

        user = get_user_model()

        if not user.objects.filter(username=USERNAME, email=EMAIL).exists():
            logger.info("Creating new superuser")
            admin = user.objects.create_superuser(
            username=USERNAME, password=PASSWORD, email=EMAIL
            )
            admin.save()
        else:
            logger.info("Superuser already created!")

    dependencies = [
        ('softwares', '0001_initial'),
    ]

    operations = [migrations.RunPython(generate_superuser)]




