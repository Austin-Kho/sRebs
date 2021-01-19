from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import intcomma
from import_export.admin import ImportExportMixin

from .models import (Project, UnitType, UnitFloorType,
                     ContractUnit, UnitNumber, ProjectBudget,
                     Site, SiteOwner, SiteOwnshipRelationship, SiteContract)
from .forms import UnitTypeForm


class ProjectAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'kind', 'num_unit', 'build_size', 'area_usage')
    list_display_links = ('name',)


class UnitTypeAdmin(ImportExportMixin, admin.ModelAdmin):
    form = UnitTypeForm
    list_display = ('id', 'project', 'name', 'styled_color', 'average_price', 'num_unit')
    list_display_links = ('project', 'name',)
    list_editable = ('average_price', 'num_unit')

    def styled_color(self, obj):
        return format_html(f'<div style="width:15px; background:{obj.color};">&nbsp;</div>')

    styled_color.short_description = '타입색상'


class UnitFloorTypeAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'project', 'alias_name', 'start_floor', 'end_floor')
    list_display_links = ('project', 'alias_name',)


class ContractUnitAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'project', 'unit_code', 'unit_type', 'contract')
    search_fields = ('unit_code',)
    list_display_links = ('project', 'unit_code',)


class UnitNumberAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'project', '__str__', 'contract_unit', 'unit_type', 'floor_type', 'bldg_line', 'floor_no', 'is_hold', 'hold_reason')
    search_fields = ('bldg_no', 'bldg_unit_no')
    list_display_links = ('project', '__str__',)


class ProjectBudgetAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'project', 'account_d1', 'account_d2', 'budget')
    list_display_links = ('project', 'account_d1', 'account_d2')
    list_editable = ('budget',)


class SiteAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('order', 'project', '__str__', 'site_purpose', 'official_area', 'returned_area', 'rights_restrictions', 'dup_issue_date', 'created_at', 'updated_at')
    list_display_links = ('project', '__str__',)
    list_editable = ('official_area', 'returned_area')
    search_fields = ('__str__',)


class SiteOwnerAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'owner', 'date_of_birth', 'phone1', 'phone2', 'zipcode', 'address1', 'address2', 'address3', 'own_sort')
    list_display_links = ('owner',)
    search_fields = ('owner', 'own_sort')
    list_filter = ('own_sort',)

class SiteOwnshipRelationshipAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'site', 'site_owner', 'ownership_ratio', 'owned_area', 'acquisition_date')
    list_display_links = ('site', 'site_owner')
    list_editable = ('ownership_ratio', 'owned_area', 'acquisition_date')

class SiteContractAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'owner', 'formatted_price', 'contract_date', 'acc_bank', 'acc_number', 'acc_owner', 'remain_pay_is_paid', 'ownership_completion')
    list_display_links = ('owner',)

    def formatted_price(self, obj):
        price = intcomma(obj.total_prices)
        return f'{price} 원'

    formatted_price.short_description = '총매매대금'


admin.site.register(Project, ProjectAdmin)
admin.site.register(UnitType, UnitTypeAdmin)
admin.site.register(UnitFloorType, UnitFloorTypeAdmin)
admin.site.register(ContractUnit, ContractUnitAdmin)
admin.site.register(UnitNumber, UnitNumberAdmin)
admin.site.register(ProjectBudget, ProjectBudgetAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(SiteOwner, SiteOwnerAdmin)
admin.site.register(SiteOwnshipRelationship, SiteOwnshipRelationshipAdmin)
admin.site.register(SiteContract, SiteContractAdmin)
