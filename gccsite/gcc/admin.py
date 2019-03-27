from adminsortable.admin import SortableTabularInline, NonSortableParentAdmin
from django.db.models import Q
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from gcc.models import (Answer, Applicant, ApplicantLabel, ApplicantStatusTypes,
                        Corrector, Edition, Event, EventWish, Form, Question,
                        SubscriberEmail, Sponsor)



admin.site.register([ApplicantLabel, Edition, SubscriberEmail, Question])

class QuestionInline(SortableTabularInline):
    model = Form.question_list.through
    extra = 1

@admin.register(Form)
class FormAdmin(NonSortableParentAdmin):
    inlines = [QuestionInline]

class EventWishesInline(admin.TabularInline):
    model = EventWish

class ApplicationStatusFilter(admin.SimpleListFilter):
    title = _('status')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return ((str(item.value), name)
                for name, item in ApplicantStatusTypes.__members__.items())

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        if int(self.value()) == ApplicantStatusTypes.incomplete.value:
            return queryset.filter(Q(eventwish__status=0) | Q(eventwish=None))

        return queryset.filter(eventwish__status=0)

@admin.register(Applicant)
class ApplicationAdmin(admin.ModelAdmin):
    Applicant.get_status_display.short_description = _('status')

    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    list_display = ('user', 'edition', 'get_status_display')
    list_filter = ('edition', ApplicationStatusFilter, 'assignation_wishes__center')
    readonly_fields = ('user', 'edition')
    fieldsets = (
        (None, {'fields': ('user', 'edition', )}),
        (_('Review'), {'fields': ('labels', )}))
    inlines = [EventWishesInline]


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
