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
from . views import BooksListView, BooksDetailView
from . views import BooksCreateView, BooksUpdateView, BooksDeleteView

from . views import SubjectsIndexView, SubjectsDetailView
from . views import SubjectsCreateView, SubjectsUpdateView, SubjectsDeleteView

app_name = 'books'

urlpatterns = [
    path('', BooksListView.as_view(), name='index'),
    path('<int:pk>/', BooksDetailView.as_view(), name='detail'),
    path('add/', BooksCreateView.as_view(), name='add'),
    path('edit/<int:pk>/', BooksUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', BooksDeleteView.as_view(), name='delete'),

    path('<int:book>/subject/', SubjectsIndexView.as_view(), name='subject_index'),
    path('<int:book>/subject/<int:pk>/', SubjectsDetailView.as_view(), name='subject_detail'),
    path('<int:book>/subject/add/', SubjectsCreateView.as_view(), name='subject_add'),
    path('<int:book>/subject/edit/<int:pk>/', SubjectsUpdateView.as_view(), name='subject_edit'),
    path('<int:book>/subject/delete/<int:pk>/', SubjectsDeleteView.as_view(), name='subject_delete'),
]
