from django.db import models
from django.conf import settings


class SalesBillIssue(models.Model):
    project = models.ForeignKey('rebs_project.Project', on_delete=models.PROTECT, verbose_name='프로젝트')
    now_payment_order = models.ForeignKey('rebs_cash.InstallmentPaymentOrder', on_delete=models.PROTECT, verbose_name='현재 발행회차')
    host_name = models.CharField('시행자명', max_length=20)
    host_tel = models.CharField('시행사 전화', max_length=13)
    agency = models.CharField('대행사명', max_length=20, blank=True)
    agency_tel = models.CharField('대행사 전화', max_length=13, blank=True)
    bank_account1 = models.CharField('수납은행[1]', max_length=20)
    bank_number1 = models.CharField('계좌번호[1]', max_length=20)
    bank_host1 = models.CharField('예금주[1]', max_length=15)
    bank_account2 = models.CharField('수납은행[2]', max_length=20, blank=True)
    bank_number2 = models.CharField('계좌번호[2]', max_length=20, blank=True)
    bank_host2 = models.CharField('예금주[2]', max_length=15, blank=True)
    zipcode = models.CharField('우편번호', max_length=5)
    address1 = models.CharField('주소', max_length=50)
    address2 = models.CharField('상세주소', max_length=30, blank=True, default='')
    address3 = models.CharField('참고항목', max_length=30, blank=True, default='')
    title = models.CharField('고지서 제목', max_length=255)
    content = models.TextField('고지서 내용')
    register = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='등록자')
    updated_at = models.DateTimeField('최종 변경일', auto_now=True)
