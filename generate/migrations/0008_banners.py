# Generated by Django 4.1.6 on 2023-02-18 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generate', '0007_prompttext'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banners',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='img/%Y/%m/%d')),
                ('orientation', models.CharField(choices=[('Gorizontal', 'Gorizontal'), ('Vertical', 'Vertical')], max_length=50)),
            ],
        ),
    ]