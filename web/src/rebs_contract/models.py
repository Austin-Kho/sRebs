from django.db import models
from django.conf import settings


class OrderGroup(models.Model):
    project = models.ForeignKey('rebs_project.Project', on_delete=models.PROTECT, verbose_name='프로젝트')
    order_number = models.PositiveSmallIntegerField('차수')
    SORT_CHOICES = (('1', '일반분양'), ('2', '조합원'))
    sort = models.CharField('구분', max_length=1, choices=SORT_CHOICES)
    order_group_name = models.CharField('차수명', max_length=20)

    def __str__(self):
        return self.order_group_name

    class Meta:
        ordering = ['-project', 'order_number', '-id']
        verbose_name = '01. 차수 (계약그룹)'
        verbose_name_plural = '01. 차수 (계약그룹)'


class Contract(models.Model):
    project = models.ForeignKey('rebs_project.Project', on_delete=models.PROTECT, verbose_name='프로젝트')
    order_group = models.ForeignKey('OrderGroup', on_delete=models.PROTECT, verbose_name='차수')
    serial_number = models.CharField('계약 일련 번호', max_length=30, unique=True)
    activation = models.BooleanField('계약 활성 여부', default=True)
    created_at = models.DateTimeField('등록일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    register = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='등록자')

    def __str__(self):
        return f'[{self.project.id}] {self.serial_number}'

    class Meta:
        ordering = ('-project', 'id')
        verbose_name = '02. 계약 정보'
        verbose_name_plural = '02. 계약 정보'


class Contractor(models.Model):
    contract = models.OneToOneField('Contract', on_delete=models.PROTECT, verbose_name='계약 정보')
    name = models.CharField('계약자명', max_length=20)
    birth_date = models.DateField('생년월일', null=True, blank=True)
    GENDER_CHOICES = (('M', '남자'), ('F', '여자'))
    gender = models.CharField('성별', max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    is_registed = models.BooleanField('인가등록여부', default=False, blank=True)
    STATUS_CHOICES = (('1', '청약'), ('2', '계약'), ('3', '청약해지'), ('4', '계약해지'))
    status = models.CharField('현재상태', max_length=1, choices=STATUS_CHOICES)
    reservation_date = models.DateField('청약일자', null=True, blank=True)
    contract_date = models.DateField('계약일자', null=True, blank=True)
    note = models.TextField('비고', blank=True)
    created_at = models.DateTimeField('등록일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    register = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='등록자')

    def __str__(self):
        return f'{self.name}({self.contract.serial_number})'

    class Meta:
        verbose_name = '03. 계약자 정보'
        verbose_name_plural = '03. 계약자 정보'


class ContractorAddress(models.Model):
    contractor = models.OneToOneField('Contractor', on_delete=models.PROTECT, verbose_name='계약자 정보')
    id_zipcode = models.CharField('우편번호', max_length=5)
    id_address1 = models.CharField('주민등록 주소', max_length=50)
    id_address2 = models.CharField('상세주소', max_length=30, blank=True, default='')
    id_address3 = models.CharField('참고항목', max_length=30, blank=True, default='')
    dm_zipcode = models.CharField('우편번호', max_length=5)
    dm_address1 = models.CharField('우편송부 주소', max_length=50)
    dm_address2 = models.CharField('상세주소', max_length=30, blank=True, default='')
    dm_address3 = models.CharField('참고항목', max_length=30, blank=True, default='')
    created_at = models.DateTimeField('등록일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    register = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='등록자')

    def __str__(self):
        return f'[주소] - {self.contractor}'

    class Meta:
        verbose_name = '04. 계약자 주소'
        verbose_name_plural = '04. 계약자 주소'


class ContractorContact(models.Model):
    contractor = models.OneToOneField('Contractor', on_delete=models.PROTECT, verbose_name='계약자 정보')
    cell_phone = models.CharField('휴대전화', max_length=13)
    home_phone = models.CharField('집 전화', max_length=13, null=True, blank=True)
    other_phone = models.CharField('기타 전화', max_length=13, null=True, blank=True)
    email = models.EmailField('이메일', null=True, blank=True)
    created_at = models.DateTimeField('등록일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    register = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='등록자')

    def __str__(self):
        return f'[연락처] - {self.contractor}'

    class Meta:
        verbose_name = '05. 계약자 연락처'
        verbose_name_plural = '05. 계약자 연락처'

class ContractorRelease(models.Model):
    project = models.ForeignKey('rebs_project.Project', on_delete=models.PROTECT, verbose_name='프로젝트')
    contractor = models.OneToOneField('Contractor', on_delete=models.CASCADE, verbose_name='계약자 정보')
    status = models.CharField('상태', choices=(('3', '신청 중'), ('4', '처리완료'), ('5', '신청취소')), max_length=1)
    refund_amount = models.PositiveIntegerField('환불(예정)금액', null=True, blank=True)
    refund_account_bank = models.CharField('환불계좌(은행)', max_length=20, blank=True)
    refund_account_number = models.CharField('환불계좌(번호)', max_length=30, blank=True)
    refund_account_depositor = models.CharField('환불계좌(예금주)', max_length=30, blank=True)
    request_date = models.DateField('해지신청일')
    completion_date = models.DateField('해지(환불)처리일', null=True, blank=True)
    note = models.TextField('비고', blank=True)
    created_at = models.DateTimeField('등록일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    register = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='등록자')

    def __str__(self):
        return f'{self.contractor}'

    class Meta:
        verbose_name = '06. 계약 해지 정보'
        verbose_name_plural = '06. 계약 해지 정보'
