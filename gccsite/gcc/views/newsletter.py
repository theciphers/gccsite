# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

from django.contrib import messages
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

from gcc.models import SubscriberEmail


class UnsubscribeView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('gcc:index')

    def get(self, request, *args, **kwargs):
        try:
            subscriber = SubscriberEmail.objects.get(email=kwargs['email'])

            if subscriber.unsubscribe_token == kwargs['token']:
                subscriber.delete()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    _('Successfully unsubscribed from newsletter.'),
                )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    _('Failed to unsubscribe: wrong token.'),
                )
        except SubscriberEmail.DoesNotExist:
            messages.add_message(
                request,
                messages.ERROR,
                _('Failed to unsubscribe: unregistered address'),
            )

        return super().get(request, *args, **kwargs)
