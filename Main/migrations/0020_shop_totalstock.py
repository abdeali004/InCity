# Generated by Django 3.1.4 on 2021-01-31 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0019_auto_20210131_1137'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='totalStock',
            field=models.IntegerField(default=0),
        ),
    ]
