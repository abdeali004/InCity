# Generated by Django 3.1.4 on 2021-01-25 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0010_auto_20210125_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='description',
            field=models.TextField(default=''),
        ),
    ]
