# Generated by Django 3.2.13 on 2022-07-25 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile_user', '0005_roommember'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='user',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
