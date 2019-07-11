# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

import os
from datetime import date

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.formats import date_format

from centers.models import Center


class Edition(models.Model):
    year = models.PositiveIntegerField(primary_key=True, unique=True)
    signup_form = models.ForeignKey('Form', on_delete=models.CASCADE)

    @cached_property
    def poster_url(self):
        """Gets poster's URL if it exists else return None"""
        name = 'poster.full.jpg'
        path = self.file_path(name)

        if not os.path.exists(path):
            return None

        return self.file_url(name)

    def file_path(self, *tail):
        """Gets file's absolute path"""
        return os.path.abspath(
            os.path.join(settings.GCC_REPOSITORY_PATH, str(self.year), *tail)
        )

    def file_url(self, *tail):
        """Gets file's URL"""
        return os.path.join(
            settings.STATIC_URL,
            settings.GCC_REPOSITORY_STATIC_PREFIX,
            str(self.year),
            *tail,
        )

    @staticmethod
    def current():
        """Gets current edition"""
        return Edition.objects.latest()

    def subscription_is_open(self):
        """Is there still one event open for subscription"""
        current_events = Event.objects.filter(
            edition=self,
            signup_start__lt=date.today(),
            signup_end__gte=date.today(),
        )
        return current_events.exists()

    def __str__(self):
        return str(self.year)

    class Meta:
        ordering = ['-year']
        get_latest_by = ['year']


class Event(models.Model):
    center = models.ForeignKey(Center, on_delete=models.CASCADE)
    edition = models.ForeignKey(Edition, on_delete=models.CASCADE)
    is_long = models.BooleanField(default=True)
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()
    signup_start = models.DateTimeField()
    signup_end = models.DateTimeField()
    signup_form = models.ForeignKey(
        'Form', on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return (
            self.event_start.strftime('%Y-%m-%d')
            + ' - '
            + self.event_start.strftime('%Y-%m-%d')
            + ' '
            + str(self.center)
        )

    def csv_name(self):
        return (
            self.event_start.strftime('%Y-%m-%d')
            + '_'
            + str(self.center).replace(' ', '_')
        )

    def short_description(self):
        return '{name} – {start} to {end}'.format(
            name=self.center.name,
            start=date_format(self.event_start, "SHORT_DATE_FORMAT"),
            end=date_format(self.event_end, "SHORT_DATE_FORMAT"),
        )
