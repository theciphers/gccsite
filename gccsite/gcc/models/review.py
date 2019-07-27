# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

from django.conf import settings
from django.db import models

from .edition import Event


class ReviewLabel(models.Model):
    """Labels to comment on an applicant"""

    display = models.CharField(max_length=10)

    def __str__(self):
        return self.display


class Corrector(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='correctors'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.user)
