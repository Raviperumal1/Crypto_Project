# Generated by Django 5.0.1 on 2024-06-28 02:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0012_remove_carddetails_transaction'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CardDetails',
        ),
    ]
