import hashlib
from datetime import datetime
from django.db import models
from django.urls import reverse_lazy
from mdeditor.fields import MDTextField
from django.template.defaultfilters import slugify

from django.conf import settings


class Book(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='등록자')
    title = models.CharField('제목', max_length=100)
    disclosure = models.BooleanField('공개 허용 여부', default=False)
    author = models.CharField('저자', max_length=50)
    translator = models.CharField('번역자', max_length=50, null=True, blank=True)
    publisher = models.CharField('출판사', max_length=50)
    pub_date = models.DateField('출간일 (최종)', null=True, blank=True)
    # description = models.TextField(blank=True, null=True)
    description = MDTextField('책설명', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = '1. 도서'
        verbose_name_plural = '1. 도서'

    def __str__(self):
        return self.title


class Subject(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='등록자')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    seq = models.PositiveSmallIntegerField('순서')
    title = models.CharField('단원 명칭', max_length=100)

    class SubLevel(models.IntegerChoices):
        _1 = 1
        _2 = 2
        _3 = 3
        _4 = 4
        _5 = 5

    level = models.IntegerField('단원 레벨', choices=SubLevel.choices)
    content = MDTextField('단원 내용', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('book', 'seq')
        verbose_name = '2. 단원'
        verbose_name_plural = '2. 단원'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy('books:subject_detail', args=(self.book_id, self.pk))

    # created_at 기준으로 이전 포스트 반환
    def get_previous_post(self):
        previous_seq = self.seq - 1
        return Subject.objects.get(book=self.book_id, seq=previous_seq)

    # created_at 기준으로 다음 포스트 반환
    def get_next_post(self):
        next_seq = self.seq + 1
        return Subject.objects.get(book=self.book_id, seq=next_seq)

def get_image_filename(instance, filename):
    today = datetime.today().strftime('%Y-%m-%d')
    hash_value = hashlib.md5().hexdigest()
    return f"editor/{today}_{hash_value}_{filename}"

class Images(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, default=None)
    image = models.ImageField(upload_to=get_image_filename, verbose_name='Image')
