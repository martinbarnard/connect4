# Generated by Django 2.0.2 on 2018-02-24 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connect4', '0002_auto_20180222_2121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='status',
            field=models.CharField(default='active', max_length=10),
        ),
    ]
