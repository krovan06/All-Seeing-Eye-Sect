# Generated by Django 4.2.18 on 2025-02-17 02:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0023_alter_comment_editable_until_accountrecoverytoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='editable_until',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 17, 2, 27, 35, 613498, tzinfo=datetime.timezone.utc)),
        ),
    ]
