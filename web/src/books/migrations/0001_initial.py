# Generated by Django 3.1.5 on 2021-01-16 13:00

import books.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mdeditor.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='제목')),
                ('disclosure', models.BooleanField(default=False, verbose_name='공개 허용 여부')),
                ('author', models.CharField(max_length=50, verbose_name='저자')),
                ('translator', models.CharField(blank=True, max_length=50, null=True, verbose_name='번역자')),
                ('publisher', models.CharField(max_length=50, verbose_name='출판사')),
                ('pub_date', models.DateField(blank=True, null=True, verbose_name='출간일 (최종)')),
                ('description', mdeditor.fields.MDTextField(blank=True, null=True, verbose_name='책설명')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='등록자')),
            ],
            options={
                'verbose_name': '1. 도서',
                'verbose_name_plural': '1. 도서',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seq', models.PositiveSmallIntegerField(verbose_name='순서')),
                ('title', models.CharField(max_length=100, verbose_name='단원 명칭')),
                ('level', models.IntegerField(choices=[(1, ' 1'), (2, ' 2'), (3, ' 3'), (4, ' 4'), (5, ' 5')], verbose_name='단원 레벨')),
                ('content', mdeditor.fields.MDTextField(blank=True, verbose_name='단원 내용')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.book')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='등록자')),
            ],
            options={
                'verbose_name': '2. 단원',
                'verbose_name_plural': '2. 단원',
                'ordering': ('book', 'seq'),
            },
        ),
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=books.models.get_image_filename, verbose_name='Image')),
                ('subject', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='books.subject')),
            ],
        ),
    ]
