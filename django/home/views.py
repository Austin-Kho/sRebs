from django.views.generic import TemplateView, RedirectView
from django.views.generic.edit import CreateView
from account.forms import UserCreationForm
from django.urls import reverse_lazy


class IndexView(RedirectView):
    url = '/rebs/dashboard/'


class UserCreateView(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register_done')


class UserCreateDoneTV(TemplateView):
    template_name = 'registration/register_done.html'
