# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

from datetime import datetime

from django.contrib import auth, messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView

from gcc.forms import ApplicationWishesForm, CombinedApplicantUserForm
from gcc.models import Applicant, Edition, Event, EventWish
from gcc.models.applicant import StatusTypes
from rules.contrib.views import PermissionRequiredMixin


class SummaryView(PermissionRequiredMixin, DetailView):
    model = auth.get_user_model()
    context_object_name = 'shown_user'
    template_name = 'gcc/application/summary.html'
    permission_required = 'users.edit'
    success_url = reverse_lazy("gcc:summary")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shown_user = context[self.context_object_name]

        context.update(
            {
                'shown_user': shown_user,
                'current_edition': Edition.current(),
                'applicant': get_object_or_404(Applicant, user=shown_user),
                'has_applied_to_current': Applicant.objects.filter(
                    user=shown_user, edition=Edition.current()
                ),
            }
        )
        return context

    def get(self, request, *args, **kwargs):
        result = super().get(request, *args, **kwargs)
        if not self.object.is_active and not self.request.user.is_staff:
            raise Http404()
        return result


class ValidationView(PermissionRequiredMixin, DetailView):
    model = auth.get_user_model()
    context_object_name = 'shown_user'
    template_name = 'gcc/application/validation.html'
    permission_required = 'users.edit'

    def get(self, request, *args, **kwargs):
        result = super().get(request, *args, **kwargs)
        if not self.object.is_active and not self.request.user.is_staff:
            raise Http404()
        return result

    # TODO: remove redondancy of get
    def get_context_data(self, **kwargs):
        applicant = get_object_or_404(
            Applicant, user=self.request.user, edition=self.kwargs['edition']
        )
        context = super().get_context_data(**kwargs)
        context['applicant'] = applicant
        return context

    def get_success_url(self):
        return reverse(
            'gcc:application_summary', kwargs={'pk': self.request.user.pk}
        )

    def post(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        applicant = get_object_or_404(
            Applicant, user=self.request.user, edition=kwargs['edition']
        )

        if not applicant.has_complete_application():
            messages.add_message(
                request,
                messages.ERROR,
                _(
                    'Failed to validate your application, your '
                    'profile is incomplete.'
                ),
            )
        else:
            applicant.validate_current_wishes()
            messages.add_message(
                request,
                messages.SUCCESS,
                _('Successfully validated your application.'),
            )

        if not self.object.is_active and not self.request.user.is_staff:
            raise Http404()

        return HttpResponseRedirect(
            reverse(
                'gcc:application_summary', kwargs={'pk': self.request.user.pk}
            )
        )


class FormView(FormView):
    template_name = 'gcc/application/form.html'
    form_class = CombinedApplicantUserForm

    def dispatch(self, request, *args, **kwargs):
        # Redirect if already validated for this year.
        if request.user.is_anonymous:
            return super().dispatch(request, *args, **kwargs)

        edition = get_object_or_404(Edition, year=kwargs['edition'])
        applicant = Applicant.for_user_and_edition(self.request.user, edition)

        if applicant.is_locked():
            messages.add_message(
                request,
                messages.ERROR,
                _(
                    'Your application has already been validated, if you '
                    'really want to change something contact us by email.'
                ),
            )
            return HttpResponseRedirect(
                reverse(
                    'gcc:application_summary',
                    kwargs={'pk': self.request.user.pk},
                )
            )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applicant'] = get_object_or_404(
            Applicant,
            edition__year=self.kwargs['edition'],
            user=self.request.user,
        )
        return context

    def get_object(self, queryset=None):
        # available from prologin.middleware.ContestMiddleware
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        kwargs['user'] = self.request.user
        kwargs['edition'] = get_object_or_404(
            Edition, year=self.kwargs['edition']
        )
        return kwargs

    def get_success_url(self):
        return reverse(
            'gcc:application_wishes',
            kwargs={
                'edition': get_object_or_404(
                    Edition, year=self.kwargs['edition']
                )
            },
        )

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class WishesView(FormView, PermissionRequiredMixin):
    template_name = 'gcc/application/wishes.html'
    form_class = ApplicationWishesForm
    permission_required = 'gcc.can_edit_own_application'

    def get_permission_object(self):
        return get_object_or_404(
            Applicant,
            user=self.request.user,
            edition__year=self.kwargs['edition'],
        )

    def get_success_url(self):
        return reverse(
            'gcc:application_summary', kwargs={'pk': self.request.user.pk}
        )

    def get_form_kwargs(self):
        # Specify the edition to the form's constructor
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                'edition': get_object_or_404(
                    Edition, year=self.kwargs['edition']
                ),
                'user': self.request.user,
            }
        )
        return kwargs

    def get_initial(self):
        event_wishes = EventWish.objects.filter(
            applicant__user=self.request.user,
            applicant__edition__year=self.kwargs['edition'],
        )
        initials = {}

        for wish in event_wishes:
            assert wish.order in [1, 2, 3]
            field_name = 'priority' + str(wish.order)
            initials[field_name] = wish.event.pk

        return initials

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.filter(
            signup_start__lt=datetime.now(),
            signup_end__gt=datetime.now(),
            edition=self.kwargs['edition'],
        ).order_by('event_start')
        return context

    def form_valid(self, form):
        edition = get_object_or_404(Edition, year=self.kwargs['edition'])
        form.save(self.request.user, edition)
        return super().form_valid(form)


class ConfirmVenueView(PermissionRequiredMixin, RedirectView):
    permission_required = 'users.edit'

    def get_permission_object(self):
        return get_object_or_404(
            EventWish, pk=self.kwargs['wish']
        ).applicant.user

    def get_redirect_url(self, *args, **kwargs):
        wish = get_object_or_404(EventWish, pk=kwargs['wish'])
        return reverse(
            'gcc:application_summary', kwargs={'pk': wish.applicant.user.pk}
        )

    def get(self, request, *args, **kwargs):
        if self.has_permission():
            wish = get_object_or_404(EventWish, pk=kwargs['wish'])

            if wish.status == StatusTypes.accepted.value:
                wish.status = StatusTypes.confirmed.value
                wish.save()
                messages.add_message(
                    self.request,
                    messages.SUCCESS,
                    _('Confirmation completed, thank you for your help!'),
                )

        return super().get(request, *args, **kwargs)
