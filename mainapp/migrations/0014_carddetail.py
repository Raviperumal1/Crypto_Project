# Generated by Django 5.0.1 on 2024-07-02 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0013_delete_carddetails'),
    ]

    operations = [
        migrations.CreateModel(
            name='CardDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.CharField(max_length=16)),
                ('expiry_date', models.CharField(max_length=5)),
                ('cvv', models.CharField(max_length=3)),
            ],
        ),
    ]
