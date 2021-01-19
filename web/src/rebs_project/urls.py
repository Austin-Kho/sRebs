from django.urls import path
from .views import *


app_name = 'project'

urlpatterns = [
    path('', ProjectList.as_view(), name='index'),
    path('settings-ordergroup/', SettingsOrderGroup.as_view(), name='set-ordergroup'),
    path('settings-unit-type/', SettingsUnitType.as_view(), name='set-unit-type'),
    path('settings-floor-type/', SettingsFloorType.as_view(), name='set-floor-type'),
    path('settings-sales-price/', SettingsSalesPrice.as_view(), name='set-sales-price'),
    path('settings-payment-order/', SettingsPaymentOrder.as_view(), name='set-payment-order'),
    path('settings-payment-amount/', SettingsPaymentAmount.as_view(), name='set-payment-amount'),
    path('site-manage/', SiteManage.as_view(), name='site'),
    path('site-del/<int:pk>/', siteDelete, name='site-del'),
    path('site-owner/', SiteOwnerManage.as_view(), name='site-owner'),
    path('site-relation/', siteRelationshipUpdate, name='site-relation'),
    path('site-relation-delete/<int:pk>', siteRelationshipDelete, name='site-relateion-delete'),
    path('site-contract/', SiteContractManage.as_view(), name='site-contract'),
    path('site-contract-delete/<int:pk>', siteContractDelete, name='site-contract-delete'),
]
