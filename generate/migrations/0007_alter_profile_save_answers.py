# Generated by Django 4.1.6 on 2023-02-07 01:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generate', '0006_alter_profile_save_answers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='save_answers',
            field=models.JSONField(blank=True),
        ),
    ]
