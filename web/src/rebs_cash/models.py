from django.db import models
from django.conf import settings


class BankCode(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class CompanyBankAccount(models.Model):
    company = models.ForeignKey('rebs_company.Company', on_delete=models.PROTECT, verbose_name='회사정보')
    division = models.ForeignKey('rebs_company.Department', on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name='부서정보')
    bankcode = models.ForeignKey(BankCode, on_delete=models.PROTECT, verbose_name='은행코드')
    alias_name = models.CharField('계좌별칭', max_length=20)
    number = models.CharField('계좌번호', max_length=30, blank=True)
    holder = models.CharField('예금주', max_length=20, blank=True)
    open_date = models.DateField('개설일자', null=True, blank=True)
    note = models.CharField('비고', max_length=50, blank=True)
    inactive = models.BooleanField('비활성 여부', default=False)

    def __str__(self):
        return self.alias_name

    class Meta:
        ordering = ['id']
        verbose_name = "01. 본사 관리계좌"
        verbose_name_plural = "01. 본사 관리계좌"


class CashBook(models.Model):
    company = models.ForeignKey('rebs_company.Company', on_delete=models.PROTECT, verbose_name='회사정보')
    CATEGORY1_CHOICES = (('1', '입금'), ('2', '출금'), ('3', '대체'))
    cash_category1 = models.CharField('구분', max_length=1, choices=CATEGORY1_CHOICES)
    CATEGORY2_CHOICES = (('1', '자산'), ('2', '부채'), ('3', '자본'), ('4', '수익'), ('5', '비용'), ('6', '대체'))
    cash_category2 = models.CharField('계정', max_length=1, choices=CATEGORY2_CHOICES, null=True, blank=True)
    account = models.ForeignKey('rebs.AccountSubD3', on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='세부계정')
    content = models.CharField('적요', max_length=100)
    trader = models.CharField('거래처', max_length=30, blank=True)
    bank_account = models.ForeignKey(CompanyBankAccount, on_delete=models.PROTECT, verbose_name='거래계좌')
    income = models.PositiveBigIntegerField('입금액', null=True, blank=True)
    outlay = models.PositiveBigIntegerField('출금액', null=True, blank=True)
    EVIDENCE_CHOICES = (
        ('0', '증빙 없음'), ('1', '세금계산서'), ('2', '계산서(면세)'), ('3', '신용카드전표'), ('4', '현금영수증'), ('5', '간이영수증'))
    evidence = models.CharField('증빙 자료', max_length=1, choices=EVIDENCE_CHOICES, default='0', blank=True)
    note = models.CharField('비고', max_length=255, blank=True, default='')
    deal_date = models.DateField('거래일자')
    recoder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='등록자')
    created_at = models.DateTimeField('등록일시', auto_now_add=True)
    updated_at = models.DateTimeField('수정일시', auto_now=True)

    def __str__(self):
        return f'{self.id}. {self.cash_category1}'

    class Meta:
        ordering = ['-deal_date', '-id']
        verbose_name = '02. 본사 입출금거래'
        verbose_name_plural = '02. 본사 입출금거래'


class ProjectBankAccount(models.Model):
    project = models.ForeignKey('rebs_project.Project', on_delete=models.PROTECT, verbose_name='프로젝트')
    bankcode = models.ForeignKey(BankCode, on_delete=models.PROTECT, verbose_name='은행코드')
    alias_name = models.CharField('계좌별칭', max_length=20)
    number = models.CharField('계좌번호', max_length=30, blank=True)
    holder = models.CharField('예금주', max_length=20, blank=True)
    open_date = models.DateField('개설일자', null=True, blank=True)
    note = models.CharField('비고', max_length=50, blank=True)
    inactive = models.BooleanField('비활성 여부', default=False)
    directpay = models.BooleanField('용역비 직불 여부', default=False)

    def __str__(self):
        return self.alias_name

    class Meta:
        ordering = ['id']
        verbose_name = "03. 프로젝트 관리계좌"
        verbose_name_plural = "03. 프로젝트 관리계좌"


class ProjectCashBook(models.Model):
    project = models.ForeignKey('rebs_project.Project', on_delete=models.PROTECT, verbose_name='프로젝트')
    CATEGORY1_CHOICES = (('1', '입금'), ('2', '출금'), ('3', '대체'))
    cash_category1 = models.CharField('구분', max_length=1, choices=CATEGORY1_CHOICES)  # icp=True -> 1=수납 or 2=환불
    project_account_d1 = models.ForeignKey('rebs.ProjectAccountD1', on_delete=models.PROTECT, null=True, blank=True, verbose_name='현장 계정')
    project_account_d2 = models.ForeignKey('rebs.ProjectAccountD2', on_delete=models.PROTECT, null=True, blank=True, verbose_name='현장 세부계정')
    is_record_separate = models.BooleanField('상세 분리기록 등록', default=False, help_text='각기 다른 계정 항목이 1회에 같이 입/출금된 경우 이 항목을 체크')
    is_contract_payment = models.BooleanField('분양/분담금 여부', default=False)  # 분양대금여부(납입, 환불 모두 True)
    contract = models.ForeignKey('rebs_contract.Contract', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='계약일련번호')  # 계약일련번호  (프로젝트 귀속)
    installment_order = models.ForeignKey('InstallmentPaymentOrder', on_delete=models.CASCADE, null=True, blank=True, verbose_name='납부회차')  # 분할납부차수  (프로젝트 귀속)
    is_refund_closing = models.ForeignKey('rebs_contract.Contractor', on_delete=models.PROTECT, null=True, blank=True, verbose_name='환불 계약자', help_text='이 건 거래가 환불금 출금인 경우 이 건을 납부한 계약자를 선택')  # 환불 종결 여부
    content = models.CharField('적요', max_length=100, blank=True, default='')
    trader = models.CharField('거래처', max_length=30, blank=True, default='', help_text='분양대금(분담금)일 경우 반드시 해당 계좌에 기재된 입금자를 기재')  # icp=True -> 분양대금 납입자
    bank_account = models.ForeignKey(ProjectBankAccount, on_delete=models.PROTECT, verbose_name='거래계좌')  # icp=True -> 분양대금 납입계좌
    income = models.PositiveBigIntegerField('입금액', null=True, blank=True)  # icp=True -> 분양대금 납입금액
    outlay = models.PositiveBigIntegerField('출금액', null=True, blank=True)  # icp=True -> 분양대금 환불금액
    EVIDENCE_CHOICES = (('0', '증빙 없음'), ('1', '세금계산서'), ('2', '계산서(면세)'), ('3', '신용카드전표'), ('4', '현금영수증'), ('5', '간이영수증'))
    evidence = models.CharField('증빙 자료', max_length=1, choices=EVIDENCE_CHOICES, default='0')
    note = models.TextField('비고', blank=True, default='')
    deal_date = models.DateField('거래일자')
    recoder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='등록자')
    created_at = models.DateTimeField('등록일시', auto_now_add=True)
    updated_at = models.DateTimeField('수정일시', auto_now=True)

    def __str__(self):
        return f'{self.id}. {self.cash_category1}'

    class Meta:
        ordering = ['-deal_date', '-id']
        verbose_name = '04. 프로젝트 입출금거래'
        verbose_name_plural = '04. 프로젝트 입출금거래'


class SalesPriceByGT(models.Model):  # 차수별 타입별 분양가격
    project = models.ForeignKey('rebs_project.Project', on_delete=models.PROTECT, verbose_name='프로젝트')
    order_group = models.ForeignKey('rebs_contract.OrderGroup', on_delete=models.CASCADE, verbose_name='차수')
    unit_type = models.ForeignKey('rebs_project.UnitType', on_delete=models.CASCADE, verbose_name='타입')
    unit_floor_type = models.ForeignKey('rebs_project.UnitFloorType', on_delete=models.CASCADE, verbose_name='층별타입')
    price = models.PositiveIntegerField('분양가격', null=True)

    def __str__(self):
        return f'{self.price}'

    class Meta:
        ordering = ('order_group', 'unit_type', 'unit_floor_type', 'project')
        verbose_name = '05. 프로젝트 분양가 관리'
        verbose_name_plural = '05. 프로젝트 분양가 관리'


class InstallmentPaymentOrder(models.Model):  # 분할 납부 차수 등록
    project = models.ForeignKey('rebs_project.Project', on_delete=models.PROTECT, verbose_name='프로젝트')
    SORT_CHOICES = (('1', '계약금'), ('2', '중도금'), ('3', '잔금'))
    pay_sort = models.CharField('종류', max_length=1, choices=SORT_CHOICES)
    pay_code = models.PositiveSmallIntegerField('납입회차 코드', help_text='프로젝트 내에서 모든 납부회차를 고유 순서대로 숫자로 부여한다.')
    pay_time = models.PositiveSmallIntegerField('납부순서',
                                                help_text='동일 납부회차에 2가지 항목을 별도로 납부하여야 하는 경우(ex: 분담금 + 업무대행료) 하나의 납입회차 코드(ex: 1)에 2개의 납부순서(ex: 1, 2)를 등록한다.')
    pay_name = models.CharField('납부회차 명', max_length=20)
    alias_name = models.CharField('별칭 이름', max_length=20, blank=True, default='')
    is_pm_cost = models.BooleanField('PM용역비 여부', default=False)
    pay_due_date = models.DateField('납부기한일', null=True, blank=True)

    def __str__(self):
        return f'[{self.get_pay_sort_display()}] - {self.pay_name} {self.alias_name}'

    class Meta:
        ordering = ['-project', 'pay_code']
        verbose_name = '06. 납입회차 관리'
        verbose_name_plural = '06. 납입회차 관리'


class InstallmentPaymentAmount(models.Model):  # 회차별 납부액 등록
    sales_price = models.ForeignKey('SalesPriceByGT', on_delete=models.CASCADE, verbose_name='타입별 분양가')
    payment_order = models.ForeignKey('InstallmentPaymentOrder', on_delete=models.CASCADE, verbose_name='납입 회차')
    payment_amount = models.PositiveIntegerField('회차별 납부금액')

    def __str__(self):
        return f'{self.payment_amount}'

    class Meta:
        ordering = ('id',)
        verbose_name = '07. 회차별 납부금액 관리'
        verbose_name_plural = '07. 회차별 납부금액 관리'

# rebs_cash_salespricebygt
