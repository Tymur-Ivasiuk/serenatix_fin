# Generated by Django 4.1.6 on 2023-02-18 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generate', '0006_alter_questions_options_questions_my_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromptText',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
            ],
        ),
    ]
