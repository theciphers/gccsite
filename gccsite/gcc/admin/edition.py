# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

from django.contrib import admin

from gcc.models import Applicant, Corrector
from gcc.models.edition import Edition, Event
from gcc.export import export_queryset_as_csv


admin.site.register(Edition)


class CorrectorInline(admin.TabularInline):
    model = Corrector


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'edition',
        'center',
        'event_start',
        'event_end',
        'signup_start',
        'signup_end',
    ]
    list_filter = ['edition', 'center']
    inlines = [CorrectorInline]

    def incomplete_export_as_csv(self, request, queryset):
        participants = []
        for obj in queryset:
            participants += Applicant.incomplete_applicants_for(obj)
            return export_queryset_as_csv(
                participants, 'incomplete' + '_' + obj.csv_name()
            )

            incomplete_export_as_csv.short_description = (
                "Export incomplete as csv"
            )

    def pending_export_as_csv(self, request, queryset):
        participants = []
        for obj in queryset:
            participants += Applicant.acceptable_applicants_for(obj)
            return export_queryset_as_csv(
                participants, 'pending' + '_' + obj.csv_name()
            )

            pending_export_as_csv.short_description = "Export pending as csv"

    def accepted_and_confirmed_export_as_csv(self, request, queryset):
        participants = []
        for obj in queryset:
            participants += Applicant.accepted_applicants_for(
                obj
            ) + Applicant.confirmed_applicants_for(obj)
        return export_queryset_as_csv(
            participants, 'accepted_and_confirmed' + '_' + obj.csv_name()
        )

    accepted_and_confirmed_export_as_csv.short_description = (
        "Export accepted and confirmed as csv"
    )

    def rejected_export_as_csv(self, request, queryset):
        participants = []
        for obj in queryset:
            participants += Applicant.rejected_applicants_for(obj)
        return export_queryset_as_csv(
            participants, 'rejected' + '_' + obj.csv_name()
        )

    rejected_export_as_csv.short_description = "Export rejected as csv"

    actions = [
        "incomplete_export_as_csv",
        "pending_export_as_csv",
        "accepted_and_confirmed_export_as_csv",
        "rejected_export_as_csv",
    ]
