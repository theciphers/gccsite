# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

from adminsortable.admin import SortableTabularInline, NonSortableParentAdmin
from django.contrib import admin

from gcc.models.forms import Form, Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question', 'comment', 'response_type']
    search_fields = ['question', 'comment']


class QuestionInline(SortableTabularInline):
    model = Form.question_list.through
    extra = 1


@admin.register(Form)
class FormAdmin(NonSortableParentAdmin):
    inlines = [QuestionInline]
