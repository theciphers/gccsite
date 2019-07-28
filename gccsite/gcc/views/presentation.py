# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

import random
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from gcc.forms import EmailForm
from gcc.models import Edition, Event, Sponsor, SubscriberEmail
from prologin.email import send_email
from zinnia.models import Entry


class IndexView(FormView):
    template_name = "gcc/index.html"
    form_class = EmailForm
    success_url = reverse_lazy("gcc:index")

    def form_valid(self, form):
        instance, created = SubscriberEmail.objects.get_or_create(
            email=form.cleaned_data['email']
        )

        if created:
            messages.add_message(
                self.request, messages.SUCCESS, _('Subscription succeeded')
            )
            send_email(
                'gcc/mails/subscribe',
                instance.email,
                {'unsubscribe_url': instance.unsubscribe_url},
            )
        else:
            messages.add_message(
                self.request,
                messages.WARNING,
                _('Subscription failed: already subscribed'),
            )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        articles = Entry.published.prefetch_related('authors').all()[
            : settings.HOMEPAGE_ARTICLES
        ]
        context.update(
            {
                'last_edition': Edition.objects.latest(),
                'sponsors': list(Sponsor.objects.active()),
                'articles': articles,
            }
        )
        context['events'] = Event.objects.filter(
            signup_start__lt=datetime.now(),
            signup_end__gt=datetime.now(),
            edition=context['last_edition'],
        ).order_by('event_start')
        random.shuffle(context['sponsors'])
        return context


class EditionsView(TemplateView):
    template_name = "gcc/editions.html"


class PrivacyView(TemplateView):
    template_name = "gcc/privacy.html"


class RessourcesView(TemplateView):
    template_name = "gcc/resources.html"


class LearnMoreView(TemplateView):
    template_name = "gcc/learn_more.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'last_edition': Edition.objects.latest(),
                'SITE_HOST': settings.SITE_HOST,
            }
        )
        context['events'] = Event.objects.filter(
            signup_start__lt=datetime.now(),
            signup_end__gt=datetime.now(),
            edition=context['last_edition'],
        ).order_by('event_start')
        return context
