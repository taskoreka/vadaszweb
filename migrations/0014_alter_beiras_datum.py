# Generated by Django 5.0.3 on 2024-11-16 13:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_alter_beiras_datum'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beiras',
            name='datum',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
