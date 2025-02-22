# Generated by Django 4.2.18 on 2025-02-16 16:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0016_alter_comment_editable_until_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='has_new_comments',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='comment',
            name='editable_until',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 16, 16, 18, 0, 436308, tzinfo=datetime.timezone.utc)),
        ),
    ]
