from django.conf import settings
from django.contrib import messages, auth
from django.http import Http404, HttpResponse
from django.http.response import JsonResponse, StreamingHttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic.base import View, RedirectView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, FormView, ModelFormMixin, FormMixin
from django.views.generic.list import ListView
from hmac import compare_digest
from rules.contrib.views import PermissionRequiredMixin
from urllib.parse import quote as url_quote
from wsgiref.util import FileWrapper

from prologin.utils import absolute_site_url
import users.forms
import users.models


def auto_login(request, user):
    # Auto-login bullshit because we don't want to write our own backend
    if not hasattr(user, 'backend'):
        for backend in settings.AUTHENTICATION_BACKENDS:
            if user == auth.load_backend(backend).get_user(user.pk):
                user.backend = backend
                break
    if hasattr(user, 'backend'):
        auth.login(request, user)
        return True
    return False


class AnonymousRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class LoginView(auth.views.LoginView):
    template_name = 'users/login.html'
    authentication_form = users.forms.AuthenticationForm


@method_decorator([require_POST, csrf_protect, never_cache], name='dispatch')
class LogoutView(auth.views.LogoutView):
    next_page = reverse_lazy('index')


class ProfileView(DetailView):
    model = auth.get_user_model()
    context_object_name = 'shown_user'
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shown_user = context[self.context_object_name]
        context['see_private'] = (self.request.user == shown_user or
                                  self.request.user.is_staff)
        return context

    def get(self, request, *args, **kwargs):
        result = super().get(request, *args, **kwargs)
        if not self.object.is_active and not self.request.user.is_staff:
            raise Http404()
        return result


class EditUserView(PermissionRequiredMixin, UpdateView):
    model = auth.get_user_model()
    form_class = users.forms.UserProfileForm
    template_name = 'users/edit.html'
    context_object_name = 'edited_user'
    permission_required = 'users.edit'

    def get_success_url(self):
        return reverse('users:edit', args=[self.get_object().pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _("Changes saved."))
        return super().form_valid(form)


class PasswordFormMixin:
    """
    SetPasswordForm prototype is (user, *args, **kwargs) and does not use
    'instance' kwarg.  “Because fuck logic, that's why.”
        — Django
    """
    form_class = auth.forms.PasswordChangeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance', None)
        return kwargs

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.get_object(), **self.get_form_kwargs())
