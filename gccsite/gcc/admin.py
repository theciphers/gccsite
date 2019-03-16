from adminsortable.admin import SortableTabularInline, NonSortableParentAdmin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from gcc.models import (Answer, Applicant, ApplicantLabel, Corrector, Edition,
                        Event, EventWish, Form, Question, SubscriberEmail,
                        Sponsor)



admin.site.register([ApplicantLabel, Edition, SubscriberEmail, Question,
                     EventWish])

class QuestionInline(SortableTabularInline):
    model = Form.question_list.through
    extra = 1

@admin.register(Form)
class FormAdmin(NonSortableParentAdmin):
    inlines = [QuestionInline]

@admin.register(Applicant)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'edition', 'status')


@admin.register(Corrector)
class CorrectorAdmin(admin.ModelAdmin):
    list_display = ('user', 'event')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('edition', 'center', 'event_start', 'event_end',
                    'signup_start', 'signup_end')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'question', '__str__')


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'site', 'contact_position',
                    'contact_first_name', 'contact_last_name',
                    'is_active_bool',)
    list_filter = ('is_active',)
    ordering = ('name',)
    search_fields = ('name', 'description', 'comment', 'site',
                     'contact_position', 'contact_email', 'contact_first_name',
                     'contact_last_name', 'contact_phone_desk',
                     'contact_phone_mobile', 'contact_phone_fax',)

    def is_active_bool(self, obj):
        return obj.is_active
    is_active_bool.admin_order_field = 'is_active'
    is_active_bool.short_description = _("Active")
    is_active_bool.boolean = True
