# Generated by Django 4.2.17 on 2024-12-15 17:04

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Profile', '0002_request_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='request',
            name='attachment',
        ),
        migrations.AlterField(
            model_name='request',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='requests/files/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])], verbose_name='Изображение'),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('background', models.ImageField(blank=True, null=True, upload_to='backgrounds/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
