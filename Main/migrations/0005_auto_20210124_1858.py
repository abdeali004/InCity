# Generated by Django 3.1.4 on 2021-01-24 13:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0004_auto_20210124_1128'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userinfo',
            old_name='AddressPrimary',
            new_name='addressPrimary',
        ),
    ]