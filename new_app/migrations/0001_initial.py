# Generated by Django 5.1.6 on 2025-02-22 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='trap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.CharField(max_length=255)),
                ('weather', models.CharField(max_length=255)),
                ('time', models.DateTimeField()),
            ],
        ),
    ]
