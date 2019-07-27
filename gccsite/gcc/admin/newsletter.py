# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

from django.contrib import admin

from gcc.models.newsletter import SubscriberEmail


@admin.register(SubscriberEmail)
class SubscriberEmailAdmin(admin.ModelAdmin):
    search_fields = ['email']
