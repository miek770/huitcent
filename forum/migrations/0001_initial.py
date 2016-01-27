# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Avatar',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='NewPost',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Preference',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('posts_per_page', models.IntegerField(default=10)),
                ('threads_per_page', models.IntegerField(default=10)),
                ('show_todo', models.BooleanField(default=False)),
                ('show_admin', models.BooleanField(default=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Right',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('access', models.BooleanField(default=False)),
                ('admin', models.BooleanField(default=False)),
                ('pending', models.BooleanField(default=True)),
                ('forum', models.ForeignKey(to='forum.Forum')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('date', models.DateTimeField()),
                ('description', models.CharField(max_length=100)),
                ('archived', models.BooleanField(default=False)),
                ('sticky', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ToDo',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=50)),
                ('done', models.BooleanField(verbose_name='Done?', default=False)),
                ('priority', models.IntegerField(verbose_name='Priority', default=3)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.CharField(max_length=100)),
                ('archive', models.BooleanField(default=False)),
                ('category', models.ForeignKey(to='forum.Category')),
            ],
        ),
        migrations.AddField(
            model_name='thread',
            name='topic',
            field=models.ForeignKey(to='forum.Topic'),
        ),
        migrations.AddField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(to='forum.Thread'),
        ),
        migrations.AddField(
            model_name='post',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='newpost',
            name='post',
            field=models.ForeignKey(to='forum.Post'),
        ),
        migrations.AddField(
            model_name='newpost',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='category',
            name='forum',
            field=models.ForeignKey(to='forum.Forum'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='post',
            field=models.ForeignKey(to='forum.Post'),
        ),
    ]
