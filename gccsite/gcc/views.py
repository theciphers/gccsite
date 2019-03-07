import random
from datetime import date
from django.contrib import auth, messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from rules.contrib.views import PermissionRequiredMixin

from gcc.forms import (EmailForm, CombinedApplicantUserForm,
                       ApplicationWishesForm)
from gcc.models import (Applicant, Edition, Event, EventWish, SubscriberEmail,
                        Sponsor)
from prologin.email import send_email


# Editions


class EditionsView(TemplateView):
    template_name = "gcc/editions.html"


# Homepage


class IndexView(FormView):
    template_name = "gcc/index.html"
    form_class = EmailForm
    success_url = reverse_lazy("gcc:index")

    def form_valid(self, form):
        instance, created = SubscriberEmail.objects.get_or_create(
            email=form.cleaned_data['email'])

        if created:
            messages.add_message(self.request, messages.SUCCESS,
                                 _('Subscription succeeded'))
            send_email('gcc/mails/subscribe', instance.email,
                       {'unsubscribe_url': instance.unsubscribe_url})
        else:
            messages.add_message(self.request, messages.WARNING,
                                 _('Subscription failed: already subscribed'))

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'events': Event.objects.filter(event_end__gt=date.today()),
            'last_edition': Edition.objects.latest(),
            'sponsors': list(Sponsor.objects.active())
        })
        random.shuffle(context['sponsors'])
        return context


class RessourcesView(TemplateView):
    template_name = "gcc/resources.html"


# Newsletter


class NewsletterUnsubscribeView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('gcc:index')

    def get(self, request, *args, **kwargs):
        try:
            subscriber = SubscriberEmail.objects.get(
                email=kwargs['email'])

            if subscriber.unsubscribe_token == kwargs['token']:
                subscriber.delete()
                messages.add_message(
                    request, messages.SUCCESS,
                    _('Successfully unsubscribed from newsletter.'))
            else:
                messages.add_message(
                    request, messages.ERROR,
                    _('Failed to unsubscribe: wrong token.'))
        except SubscriberEmail.DoesNotExist:
            messages.add_message(
                request, messages.ERROR,
                _('Failed to unsubscribe: unregistered address'))

        return super().get(request, *args, **kwargs)


# Application


class ApplicationSummaryView(PermissionRequiredMixin, DetailView):
    model = auth.get_user_model()
    context_object_name = 'shown_user'
    template_name = 'gcc/application/summary.html'
    permission_required = 'users.edit'
    success_url = reverse_lazy("gcc:summary")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shown_user = context[self.context_object_name]

        context.update({
            'shown_user': shown_user,
            'current_edition': Edition.current(),
            'applications': Applicant.objects.filter(user=shown_user),
            'has_applied_to_current':
                Edition.current().user_has_applied(shown_user)
        })
        return context

    def get(self, request, *args, **kwargs):
        result = super().get(request, *args, **kwargs)
        if not self.object.is_active and not self.request.user.is_staff:
            raise Http404()
        return result


class ApplicationValidationView(PermissionRequiredMixin, DetailView):
    model = auth.get_user_model()
    context_object_name = 'shown_user'
    template_name = 'gcc/application/validation.html'
    permission_required = 'users.edit'

    def get(self, request, *args, **kwargs):
        result = super().get(request, *args, **kwargs)
        if not self.object.is_active and not self.request.user.is_staff:
            raise Http404()
        return result

    def get_success_url(self):
        return reverse(
            'gcc:application_summary',
            kwargs={'pk': self.request.user.pk})

    def post(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        if not self.request.user.has_complete_profile_for_application():
            messages.add_message(
                request, messages.ERROR,
                _("Failed to validate your application, "
                  "your profile is incomplete."))
        else:
            application = Applicant.objects.get(user=self.request.user,
                                                edition=kwargs['edition'])
            application.status = 1
            application.save()
            messages.add_message(request, messages.SUCCESS,
                                 _('Successfully validated your application.'))

        if not self.object.is_active and not self.request.user.is_staff:
            raise Http404()

        return HttpResponseRedirect(reverse(
            'gcc:application_summary', kwargs={'pk': self.request.user.pk}))


class ApplicationFormView(FormView):
    template_name = 'gcc/application/form.html'
    form_class = CombinedApplicantUserForm

    def __init__(self, **kwargs):
        self.edition = None
        super().__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        # redirect if already validated for this year.
        try:
            application = Applicant.objects.get(user=self.request.user,
                                                edition=kwargs['edition'])

            if application.status != 0:
                messages.add_message(
                    request, messages.ERROR,
                    _('Your application has already been validated, if you '
                      'really want to change something contact us by email.'))
                return HttpResponseRedirect(reverse(
                    'gcc:application_summary',
                    kwargs={'pk': self.request.user.pk}))
        except Applicant.DoesNotExist:
            pass

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # available from prologin.middleware.ContestMiddleware
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        kwargs['user'] = self.request.user
        kwargs['edition'] = get_object_or_404(Edition,
                                              year=self.kwargs['edition'])
        self.edition = kwargs['edition']
        return kwargs

    def get_success_url(self):
        return reverse('gcc:application_wishes',
                       kwargs={'edition': self.edition})

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ApplicationWishesView(FormView):
    template_name = 'gcc/application/wishes.html'
    form_class = ApplicationWishesForm

    def __init__(self, **kwargs):
        self.edition_year = None
        self.edition = None
        super().__init__(**kwargs)

    def get_success_url(self):
        return reverse(
            'gcc:application_summary',
            kwargs={'pk': self.request.user.pk})

    def get_form_kwargs(self):
        # Specify the edition to the form's constructor
        self.edition_year = self.kwargs['edition']
        self.edition = get_object_or_404(Edition, year=self.edition_year)

        kwargs = super().get_form_kwargs()
        kwargs.update({'edition': self.edition})
        return kwargs

    def get_initial(self):
        event_wishes = EventWish.objects.filter(
            applicant__user=self.request.user, applicant__edition=self.edition)
        initials = {}

        for wish in event_wishes:
            assert(wish.order in [1, 2, 3])
            field_name = 'priority' + str(wish.order)
            initials[field_name] = wish.event.pk

        return initials

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.filter(
            signup_start__lt=date.today(), signup_end__gt=date.today(),
            edition=self.kwargs['edition'])
        return context

    def form_valid(self, form):
        form.save(self.request.user, self.edition)
        return super().form_valid(form)