# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

import os

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from form.models import Form


class Edition(models.Model):
    year = models.PositiveIntegerField(primary_key=True, unique=True)
    signup_form = models.ForeignKey(Form, on_delete=models.CASCADE)

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

    def __str__(self):
        return str(self.year)

    class Meta:
        ordering = ['-year']
        get_latest_by = ['year']
