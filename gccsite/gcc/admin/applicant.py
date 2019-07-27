# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

from django.contrib import admin
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from gcc.models.applicant import Answer, Applicant, EventWish, StatusTypes
from gcc.export import ExportCsvMixin


class EventWishesInline(admin.TabularInline):
    model = EventWish
    max_num = 3


class AnswersInline(admin.TabularInline):
    def answer(self, obj):
        return str(obj)

    model = Answer
    can_delete = True
    extra = 0


class ApplicationStatusFilter(admin.SimpleListFilter):
    title = _('status')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            (str(item.value), name)
            for name, item in StatusTypes.__members__.items()
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        if int(self.value()) == StatusTypes.incomplete.value:
            return queryset.filter(
                Q(eventwish__status=0) | Q(eventwish=None)
            ).distinct()

        return queryset.filter(eventwish__status=self.value())


@admin.register(Applicant)
class ApplicationAdmin(admin.ModelAdmin, ExportCsvMixin):
    Applicant.get_status_display.short_description = _('status')

    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
    ]
    list_display = ['user', 'edition', 'get_status_display']
    list_filter = [
        'edition',
        ApplicationStatusFilter,
        'assignation_wishes__center',
        'assignation_wishes',
    ]
    readonly_fields = ['user', 'edition']
    fieldsets = [
        (None, {'fields': ['user', 'edition']}),
        (_('Review'), {'fields': ['labels']}),
    ]
    inlines = (EventWishesInline, AnswersInline)

    actions = ["export_as_csv"]
