# Generated by Django 5.1.1 on 2024-10-07 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_alter_rooms_options_rooms_participants'),
    ]

    operations = [
        migrations.CreateModel(
            name='visit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=250)),
            ],
        ),
    ]
