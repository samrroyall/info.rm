# Generated by Django 3.1.6 on 2021-03-12 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_auto_20210311_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='birthdate',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='height',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='weight',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
