# Generated by Django 5.0.1 on 2024-06-28 00:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0011_carddetails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carddetails',
            name='transaction',
        ),
    ]
