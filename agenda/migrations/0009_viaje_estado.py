# Generated by Django 3.0.6 on 2023-07-26 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0008_auto_20230725_2210'),
    ]

    operations = [
        migrations.AddField(
            model_name='viaje',
            name='estado',
            field=models.BooleanField(default=False),
        ),
    ]
