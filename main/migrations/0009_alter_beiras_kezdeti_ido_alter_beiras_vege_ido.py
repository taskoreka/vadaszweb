# Generated by Django 5.0.3 on 2024-11-12 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_alter_idopont_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beiras',
            name='kezdeti_ido',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='beiras',
            name='vege_ido',
            field=models.TimeField(),
        ),
    ]
