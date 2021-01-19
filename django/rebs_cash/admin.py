from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from import_export.admin import ImportExportMixin

from .models import CompanyBankAccount, ProjectBankAccount, CashBook, ProjectCashBook
from .models import SalesPriceByGT, InstallmentPaymentOrder, InstallmentPaymentAmount


class CompanyBankAccountAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'alias_name', 'division', 'bankcode', 'number', 'holder', 'open_date', 'note', 'inactive')
    list_display_links = ('alias_name',)
    list_filter = ('division', 'bankcode', 'holder')


class ProjectBankAccountAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'project', 'alias_name', 'bankcode', 'number', 'holder', 'open_date', 'note', 'inactive', 'directpay')
    list_display_links = ('project', 'alias_name',)
    list_filter = ('bankcode', 'holder')


class CashBookAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'deal_date', 'cash_category1', 'cash_category2', 'account',
                    'content', 'trader', 'bank_account', 'formatted_income', 'formatted_outlay', 'recoder')
    search_fields = ('account', 'content', 'trader', 'note')
    list_display_links = ('deal_date', 'content')

    def formatted_income(self, obj):
        return f'{intcomma(obj.income)} 원' if obj.income else '-'

    def formatted_outlay(self, obj):
        return f'{intcomma(obj.outlay)} 원' if obj.outlay else '-'

    formatted_income.short_description = '입금액'
    formatted_outlay.short_description = '출금액'



class ProjectCashBookAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'project', 'deal_date', 'cash_category1', 'project_account_d1', 'project_account_d2', 'contract',
                    'installment_order', 'content', 'trader', 'bank_account', 'formatted_income', 'formatted_outlay', 'recoder')
    search_fields = ('content', 'trader', 'note')
    list_display_links = ('project', 'deal_date')
    list_filter = ('cash_category1', 'project_account_d1', 'project_account_d2', 'is_contract_payment', 'bank_account')

    def formatted_income(self, obj):
        return f'{intcomma(obj.income)} 원' if obj.income else '-'

    def formatted_outlay(self, obj):
        return f'{intcomma(obj.outlay)} 원' if obj.outlay else '-'

    formatted_income.short_description = '입금액'
    formatted_outlay.short_description = '출금액'


class InstallmentPaymentAmountInline(ImportExportMixin, admin.TabularInline):
    model = InstallmentPaymentAmount
    extra = 1

class SalesPriceByGTAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'project', 'order_group', 'unit_type', 'unit_floor_type', 'price')
    list_display_links = ('project', 'unit_type', 'unit_floor_type')
    list_editable = ('price',)
    list_filter = ('project', 'order_group', 'unit_type')
    inlines = (InstallmentPaymentAmountInline,)


class InstallmentPaymentOrderAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'project', 'pay_name', 'pay_sort', 'pay_code', 'pay_time', 'alias_name', 'is_pm_cost', 'pay_due_date', 'project')
    search_fields = ('pay_name', 'alias_name',)
    list_editable = ('alias_name', 'is_pm_cost', 'pay_due_date')
    list_display_links = ('project', 'pay_name',)


class InstallmentPaymentAmountAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'sales_price', 'payment_order', 'payment_amount')
    list_display_links = ('sales_price', 'payment_order')
    list_editable = ('payment_amount',)
    list_filter = ('sales_price', 'payment_order',)


admin.site.register(CompanyBankAccount, CompanyBankAccountAdmin)
admin.site.register(ProjectBankAccount, ProjectBankAccountAdmin)
admin.site.register(CashBook, CashBookAdmin)
admin.site.register(ProjectCashBook, ProjectCashBookAdmin)
admin.site.register(SalesPriceByGT, SalesPriceByGTAdmin)
admin.site.register(InstallmentPaymentOrder, InstallmentPaymentOrderAdmin)
admin.site.register(InstallmentPaymentAmount, InstallmentPaymentAmountAdmin)
