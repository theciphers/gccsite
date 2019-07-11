# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

import hashlib

from django.conf import settings
from django.db import models
from django.urls import reverse


class SubscriberEmail(models.Model):
    email = models.EmailField()
    date = models.DateTimeField(auto_now_add=True)

    @property
    def unsubscribe_token(self):
        subscriber_id = str(self.id).encode()
        secret = settings.SECRET_KEY.encode()
        return hashlib.sha256(subscriber_id + secret).hexdigest()[:32]

    @property
    def unsubscribe_url(self):
        return reverse(
            'gcc:news_unsubscribe',
            kwargs={'email': self.email, 'token': self.unsubscribe_token},
        )

    def __str__(self):
        return self.email
