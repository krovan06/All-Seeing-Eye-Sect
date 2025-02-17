# Generated by Django 4.2.18 on 2025-02-17 03:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0027_alter_comment_editable_until'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='deleted_by',
            field=models.CharField(blank=True, choices=[('user', 'User'), ('system', 'System')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='editable_until',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 17, 3, 35, 47, 4314, tzinfo=datetime.timezone.utc)),
        ),
    ]
