from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from rebs_project.models import Project


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        """
        주어진 이메일, 닉네임, 비밀번호 등 개인정보로 User 인스턴스 생성
        """
        if not email:
            raise ValueError(_('Users must have an email address'))

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        """
        주어진 이메일, 닉네임, 비밀번호 등 개인정보로 User 인스턴스 생성
        단, 최상위 사용자이므로 권한을 부여한다.
        """
        user = self.create_user(
            email=email,
            password=password,
            username=username,
        )

        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, verbose_name=_('Email address'))
    username = models.CharField(max_length=30, unique=True, verbose_name=_('Username'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    date_joined = models.DateTimeField(default=timezone.now, verbose_name=_('Date joined'))
    # 이 필드는 레거시 시스템 호환을 위해 추가할 수도 있다.
    salt = models.CharField(max_length=10, blank=True, verbose_name=_('Salt'))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('-date_joined',)

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All superusers are staff
        return self.is_superuser

    get_full_name.short_description = _('Full name')


class StaffAuth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_staff = models.BooleanField('관리자로 승인', default=False, help_text='Staff(관리자) 승인 여부')
    assigned_project = models.ForeignKey(Project, related_name='assigned_project', on_delete=models.SET_NULL, null=True, verbose_name='담당 메인 프로젝트', help_text='선택한 프로젝트를 각 화면에서 기본 프로젝트로 보여줍니다.')
    allowed_projects = models.ManyToManyField(Project, related_name='allowed_projects', verbose_name='허용 프로젝트', help_text='조회 및 관리할 수 있는 프로젝트들을 선택합니다.')
    AUTH_CHOICE = (('0', '권한없음'), ('1', '읽기권한'), ('2', '쓰기권한'))
    contract = models.CharField('분양 계약 관리', max_length=1, choices=AUTH_CHOICE, default='0')
    payment = models.CharField('분양 수납 관리', max_length=1, choices=AUTH_CHOICE, default='0')
    notice = models.CharField('고객 고지 관리', max_length=1, choices=AUTH_CHOICE, default='0')
    project_cash = models.CharField('현장 자금 관리', max_length=1, choices=AUTH_CHOICE, default='0')
    project_docs = models.CharField('현장 문서 관리', max_length=1, choices=AUTH_CHOICE, default='0')
    project = models.CharField('신규 프로젝트', max_length=1, choices=AUTH_CHOICE, default='0')
    company_cash = models.CharField('본사 회계 관리', max_length=1, choices=AUTH_CHOICE, default='0')
    company_docs = models.CharField('본사 문서 관리', max_length=1, choices=AUTH_CHOICE, default='0')
    human_resource = models.CharField('본사 인사 관리', max_length=1, choices=AUTH_CHOICE, default='0')
    company_settings = models.CharField('회사 관련설정', max_length=1, choices=AUTH_CHOICE, default='0')
    auth_manage = models.CharField('권한 설정 관리', max_length=1, choices=AUTH_CHOICE, default='0')

    def __str__(self):
        return f'{self.user} :: 권한'

    class Meta:
        verbose_name = '스태프 권한'
        verbose_name_plural = '스태프 권한'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    cell_phone = models.CharField(max_length=13, blank=True)

    def __str__(self):
        return self.name
