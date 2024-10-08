# Generated by Django 5.1.1 on 2024-09-18 14:25

import django.db.models.deletion
import softwares.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SoftwareApp',
            fields=[
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('slug', models.SlugField(unique=True)),
                ('version_major', models.PositiveIntegerField()),
                ('version_minor', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_public', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Программное обеспечение на сервере',
                'verbose_name_plural': 'Программное обеспечение на сервере',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SoftwareAppFileConfigType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('is_required', models.BooleanField(default=True)),
                ('file_path', models.FilePathField()),
                ('software_app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='softwares.softwareapp')),
            ],
            options={
                'verbose_name': 'Тип конфигурации программного обеспечения на сервере',
                'verbose_name_plural': 'Типы конфигураций программного обеспечения ПО на сервере',
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='FileConfigTypeReplaceParam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=512)),
                ('default', models.CharField(blank=True, default='', max_length=256)),
                ('file_config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='softwares.softwareappfileconfigtype')),
            ],
            options={
                'verbose_name': 'Параметр автозамены внутри конфигурационного файла',
                'verbose_name_plural': 'Параметры автозамены внутри конфигурационного файла',
                'ordering': ['-pk'],
            },
        ),
        migrations.CreateModel(
            name='SoftwareAppTask',
            fields=[
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(choices=[(1, 'Not Started'), (2, 'Pending'), (3, 'Processing'), (4, 'Success'), (5, 'Error')], default=1)),
                ('status_update', models.DateTimeField(auto_now=True)),
                ('software_app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='softwares.softwareapp')),
            ],
            options={
                'verbose_name': 'Задача исполнения программного обеспечения',
                'verbose_name_plural': 'Задачи исполнения программного обеспечения',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SoftwareAppTaskFileConfig',
            fields=[
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('config_file', models.FileField(blank=True, null=True, upload_to=softwares.models.config_file_upload)),
                ('config_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='softwares.softwareappfileconfigtype')),
                ('software_app_task', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='softwares.softwareapptask')),
            ],
            options={
                'verbose_name': 'Конфигурация экземпляра запуска программного обеспечения',
                'verbose_name_plural': 'Конфигурации экземпляров запуска программного обеспечения',
            },
        ),
    ]
