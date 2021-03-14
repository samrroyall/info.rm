# Generated by Django 3.1.6 on 2021-03-13 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_auto_20210313_0305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerstat',
            name='position',
            field=models.PositiveSmallIntegerField(choices=[(1, 'attacker'), (2, 'midfielder'), (3, 'defender'), (4, 'goalkeeper'), (5, 'none')], default=5),
        ),
    ]
