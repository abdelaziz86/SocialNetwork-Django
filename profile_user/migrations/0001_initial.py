# Generated by Django 3.2.13 on 2022-07-14 18:23

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.TextField(blank=True)),
                ('city', models.TextField(blank=True)),
                ('region', models.TextField(blank=True)),
                ('country', models.TextField(blank=True)),
                ('latitude', models.FloatField(blank=True)),
                ('longitude', models.FloatField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_user', models.IntegerField()),
                ('bio', models.TextField(blank=True)),
                ('profileimg', models.ImageField(default='blank_prof_pic.png', upload_to='profile_images')),
                ('name', models.TextField(blank=True)),
                ('surname', models.TextField(blank=True)),
                ('domaine', models.TextField(blank=True)),
                ('phone', models.TextField(default='')),
                ('verified', models.IntegerField(blank=True, default=0)),
                ('type', models.IntegerField(default=1)),
                ('no_of_followers', models.IntegerField(default=0)),
                ('location', models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, to='profile_user.location')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to='post_images')),
                ('caption', models.TextField()),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('no_of_likes', models.IntegerField(default=0)),
                ('no_of_comments', models.IntegerField(default=0)),
                ('tag', models.TextField(blank=True)),
                ('fileType', models.IntegerField(default=0)),
                ('id_Profile', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='profile_user.profile')),
                ('id_User', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WorkExperience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=100)),
                ('companyName', models.TextField(blank=True)),
                ('companyImage', models.ImageField(blank=True, upload_to='post_images')),
                ('task', models.TextField()),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('worker', models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, to='profile_user.profile')),
            ],
        ),
        migrations.CreateModel(
            name='Verification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card', models.ImageField(blank=True, upload_to='verify_images')),
                ('read', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('profile', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='profile_user.profile')),
            ],
        ),
        migrations.CreateModel(
            name='Reaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('pub', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='profile_user.pub')),
                ('reacter', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='profile_user.profile')),
            ],
        ),
        migrations.CreateModel(
            name='Preaccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(default='')),
                ('surname', models.TextField(default='')),
                ('birth', models.DateField(blank=True, default=datetime.datetime.now)),
                ('email', models.TextField(default='')),
                ('phone', models.IntegerField(default='')),
                ('degree', models.TextField(default='')),
                ('sector', models.TextField(default='')),
                ('field', models.TextField(default='')),
                ('cv', models.ImageField(blank=True, upload_to='verify_images')),
                ('type', models.TextField(default='expert')),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PostComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desc', models.TextField()),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('commenter', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='profile_user.profile')),
                ('pub', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='profile_user.pub')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver', models.CharField(max_length=100)),
                ('desc', models.TextField(default='')),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('sender', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='profile_user.profile')),
            ],
        ),
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('connected', models.CharField(max_length=100)),
                ('verified', models.IntegerField(blank=True, default=0)),
                ('connecter', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='profile_user.profile')),
            ],
        ),
    ]
