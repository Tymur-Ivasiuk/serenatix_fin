# Generated by Django 4.1.6 on 2023-02-18 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generate', '0008_banners'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banners',
            name='orientation',
            field=models.CharField(choices=[('Horizontal', 'Horizontal'), ('Vertical', 'Vertical')], max_length=50),
        ),
    ]
