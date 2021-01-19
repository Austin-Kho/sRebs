"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from .views import *

app_name = 'rebs'

urlpatterns = [
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('contract/', include('rebs_contract.urls')),
    path('project/', include('rebs_project.urls')),
    path('cash-io/', include('rebs_cash.urls')),
    path('company/', include('rebs_company.urls')),
    path('notice/', include('rebs_notice.urls')),

    path('schedule/', memu2_1, name='menu2_1'),

    # pdf url
    path('pdf-bill/', ExportPdfBill.as_view(), name='pdf-bill'),
]
