# Generated by Django 4.2.18 on 2025-02-17 04:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0030_alter_comment_editable_until'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='editable_until',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 17, 4, 23, 30, 987410, tzinfo=datetime.timezone.utc)),
        ),
    ]
