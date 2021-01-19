from django.urls import path
from .views import *

app_name = 'excel'

urlpatterns = [
    path('contracts/', ExportContracts.as_view(), name='contracts'),
    path('reservations/', ExportApplicants.as_view(), name='reservations'),
    path('releases/', ExportReleases.as_view(), name='releases'),
    path('payments/', export_payments_xls, name='payments'),
    path('p-cashbooks/', export_project_cash_xls, name='p-cashbooks'),
    path('sites/', export_sites_xls, name='sites'),
    path('sites-by-owner/', export_sitesByOwner_xls, name='sites-by-owner'),
    path('sites-contracts/', export_sitesContracts_xls, name='sites-contracts'),
    path('cashbooks/', export_cashbook_xls, name='cashbooks'),
]
