# Generated by Django 4.1.6 on 2023-02-12 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('generate', '0002_remove_profile_partner_phone_number_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentStyles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('my_order', models.PositiveSmallIntegerField(db_index=True, default=0)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='generate.contenttypes')),
            ],
            options={
                'ordering': ['my_order'],
            },
        ),
        migrations.DeleteModel(
            name='LetterStyles',
        ),
        migrations.DeleteModel(
            name='PoemStyles',
        ),
    ]
