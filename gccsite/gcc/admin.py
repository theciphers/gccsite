# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

import csv

from adminsortable.admin import SortableTabularInline, NonSortableParentAdmin
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

import gcc.models as models


admin.site.register([models.ApplicantLabel, models.Edition])

# -- Mixins

"""
Snippet from https://books.agiliq.com/projects/django-admin-cookbook/en/latest/export.html

Exports data into CSV, useful for giving data back to users and exploiting big
amount of datas in dedicated softs

The model must implement get_export_data methods
"""
class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        mod = self.model
        meta = mod._meta
        fieldnames = []

        all_keys = set()

        datas = []

        # check all the cols names and perform SQL queries
        for obj in queryset:
            data = obj.get_export_data()
            datas.append(data)
            for key in data:
                if key not in all_keys:
                    fieldnames.append(key)
                    all_keys.add(key)

        # create the response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()

        for data in datas:
            row = writer.writerow(data)

        return response

    export_as_csv.short_description = "Export selected as csv"


# -- Forms

class QuestionInline(SortableTabularInline):
    model = models.Form.question_list.through
    extra = 1


@admin.register(models.Form)
class FormAdmin(NonSortableParentAdmin):
    inlines = [QuestionInline]


# -- Applicant

class EventWishesInline(admin.TabularInline):
    model = models.EventWish
    max_num = 3


class AnswersInline(admin.TabularInline):
    def answer(self, obj):
        return str(obj)

    model = models.Answer
    can_delete = True
    extra = 0


class ApplicationStatusFilter(admin.SimpleListFilter):
    title = _('status')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return ((str(item.value), name)
                for name, item in models.ApplicantStatusTypes.__members__.items())

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        if int(self.value()) == models.ApplicantStatusTypes.incomplete.value:
            return queryset.filter(
                Q(eventwish__status=0) | Q(eventwish=None)).distinct()

        return queryset.filter(eventwish__status=self.value())


@admin.register(models.Applicant)
class ApplicationAdmin(admin.ModelAdmin, ExportCsvMixin):
    models.Applicant.get_status_display.short_description = _('status')

    search_fields = ['user__username', 'user__first_name', 'user__last_name',
                     'user__email']
    list_display = ['user', 'edition', 'get_status_display']
    list_filter = ['edition', ApplicationStatusFilter,
                   'assignation_wishes__center']
    readonly_fields = ['user', 'edition']
    fieldsets = [(None, {'fields': ['user', 'edition']}),
                 (_('Review'), {'fields': ['labels']})]
    inlines = (EventWishesInline, AnswersInline)

    actions = ["export_as_csv"]

# -- Event

class CorrectorInline(admin.TabularInline):
    model = models.Corrector


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['edition', 'center', 'event_start', 'event_end',
                    'signup_start', 'signup_end']
    list_filter = ['edition', 'center']
    inlines = [CorrectorInline]


# -- Question

@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question', 'comment', 'response_type']
    search_fields = ['question', 'comment']


# -- Sponsor

@admin.register(models.Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'site', 'contact_position',
                    'contact_first_name', 'contact_last_name', 'is_active_bool']
    list_filter = ['is_active']
    ordering = ['name']
    search_fields = ['name', 'description', 'comment', 'site',
                     'contact_position', 'contact_email', 'contact_first_name',
                     'contact_last_name', 'contact_phone_desk',
                     'contact_phone_mobile', 'contact_phone_fax']

    def is_active_bool(self, obj):
        return obj.is_active

    is_active_bool.admin_order_field = 'is_active'
    is_active_bool.short_description = _("Active")
    is_active_bool.boolean = True


# Newsletter

@admin.register(models.SubscriberEmail)
class SubscriberEmailAdmin(admin.ModelAdmin):
    search_fields = ['email']
