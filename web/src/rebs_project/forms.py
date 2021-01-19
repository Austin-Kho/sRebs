from django import forms
from django.forms.models import modelformset_factory
from django.forms.widgets import TextInput
from .models import UnitType, UnitFloorType, Site, SiteOwner, SiteContract
from rebs_contract.models import OrderGroup
from rebs_cash.models import SalesPriceByGT, InstallmentPaymentOrder, InstallmentPaymentAmount


OrderGroupFormSet = modelformset_factory(OrderGroup, exclude=('project',))


class UnitTypeForm(forms.ModelForm): # admin.py use
    class Meta:
        model = UnitType
        fields = '__all__'
        widgets = {'color': TextInput(attrs={'type': 'color'})}


UnitTypeFormSet = modelformset_factory(UnitType,
                                       form=UnitTypeForm,
                                       exclude=('project',),
                                       extra=0)


UnitFloorTypeFormSet = modelformset_factory(UnitFloorType,
                                            exclude=('project',))


SalesPriceByGTFormSet = modelformset_factory(SalesPriceByGT,
                                             exclude=('project',),
                                             widgets={'order_group': forms.HiddenInput(),
                                                      'unit_type': forms.HiddenInput(),
                                                      'unit_floor_type': forms.HiddenInput()}, extra=0)


InstallmentPaymentOrderFormSet = modelformset_factory(InstallmentPaymentOrder,
                                                      exclude=('project',))


InstallmentPaymentAmountFormSet = modelformset_factory(InstallmentPaymentAmount,
                                                       exclude=('project',),
                                                       # widgets={'sales_price': forms.HiddenInput()}
                                                       )


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = '__all__'
        widgets = {'project': forms.HiddenInput()}


class SiteOwnerForm(forms.ModelForm):
    class Meta:
        model = SiteOwner
        fields = '__all__'
        widgets = {'project': forms.HiddenInput(), 'register': forms.HiddenInput()}

    def __init__(self, project, *args, **kwargs):
        super(SiteOwnerForm, self).__init__(*args, **kwargs)
        self.fields['sites'].queryset = Site.objects.filter(project=project)


class SiteContractForm(forms.ModelForm):
    class Meta:
        model = SiteContract
        fields = '__all__'
        widgets = {'project': forms.HiddenInput(), 'register': forms.HiddenInput()}

    def __init__(self, project, *args, **kwargs):
        super(SiteContractForm, self).__init__(*args, **kwargs)
        self.fields['owner'].queryset = SiteOwner.objects.filter(project=project).order_by('id')
