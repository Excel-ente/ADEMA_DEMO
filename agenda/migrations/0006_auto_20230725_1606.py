# Generated by Django 3.0.6 on 2023-07-25 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0005_remove_vendedor_codigo'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendedor',
            name='codigo',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='codigo',
            field=models.CharField(blank=True, max_length=200, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='direccion',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='nit',
            field=models.CharField(blank=True, default=1, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='nombre',
            field=models.CharField(blank=True, max_length=200, null=True, unique=True, verbose_name='Vendedor'),
        ),
    ]