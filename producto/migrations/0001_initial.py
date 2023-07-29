# Generated by Django 3.0.6 on 2020-05-19 16:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('precio', models.DecimalField(decimal_places=2, max_digits=2, max_length=4)),
                ('en_stock', models.DecimalField(decimal_places=2, max_digits=2, max_length=4)),
                ('nombre', models.CharField(max_length=100)),
                ('descripción', models.CharField(max_length=200)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='producto.Categoria')),
            ],
        ),
    ]