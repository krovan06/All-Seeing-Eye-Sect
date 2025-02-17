# Generated by Django 4.2.18 on 2025-02-17 02:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0021_alter_comment_editable_until'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='original_body',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='editable_until',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 17, 2, 16, 41, 867331, tzinfo=datetime.timezone.utc)),
        ),
        migrations.DeleteModel(
            name='AccountRecoveryToken',
        ),
    ]
