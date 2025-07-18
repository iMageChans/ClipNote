# Generated by Django 5.1.7 on 2025-07-09 07:10

import ckeditor.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BodyPart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='部位名称')),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True, verbose_name='URL别名')),
                ('description', models.TextField(blank=True, verbose_name='描述')),
            ],
            options={
                'verbose_name': '健身部位',
                'verbose_name_plural': '健身部位管理',
            },
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='动作名称')),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True, verbose_name='URL别名')),
                ('description', ckeditor.fields.RichTextField(verbose_name='动作描述')),
                ('youtube_url', models.URLField(blank=True, verbose_name='YouTube视频链接')),
                ('image', models.ImageField(blank=True, upload_to='exercises/%Y/%m/', verbose_name='动作图片')),
                ('image_width', models.PositiveIntegerField(blank=True, null=True, verbose_name='图片宽度')),
                ('image_height', models.PositiveIntegerField(blank=True, null=True, verbose_name='图片高度')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('body_part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='fitness.bodypart', verbose_name='锻炼部位')),
            ],
            options={
                'verbose_name': '健身动作',
                'verbose_name_plural': '健身动作管理',
            },
        ),
    ]
