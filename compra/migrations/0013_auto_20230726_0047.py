# Generated by Django 3.0.6 on 2023-07-26 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compra', '0012_auto_20230725_2217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compra',
            name='fecha',
            field=models.DateField(),
        ),
    ]