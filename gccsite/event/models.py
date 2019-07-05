from datetime import date

from django.db import models
from django.utils.formats import date_format

from centers.models import Center
from gcc.models import Edition
from form.models import Form


class EventQuerySet(models.QuerySet):
    def opened_for_edition(self, edition):
        return self.filter(
            edition=edition,
            signup_start__lt=date.today(),
            signup_end__gte=date.today(),
        )


class Event(models.Model):
    center = models.ForeignKey(
        Center, on_delete=models.CASCADE, related_name='migrate_event_center'
    )
    edition = models.ForeignKey(
        Edition, on_delete=models.CASCADE, related_name='migrate_event_edition'
    )

    # TODO: can it be removed ? We have enough informations to detect if a
    #       summer camp lasts for a whole week... Overwise, maybe it should be
    #       generalized for various kinds of events?
    is_long = models.BooleanField(default=True)

    event_start = models.DateTimeField()
    event_end = models.DateTimeField()
    signup_start = models.DateTimeField()
    signup_end = models.DateTimeField()

    signup_form = models.ForeignKey(Form, on_delete=models.CASCADE, null=True)

    objects = EventQuerySet.as_manager()

    @staticmethod
    def opened_for_edition(edition):
        """Return the list of events opened for the input edition"""
        return Event.objects.filter(
            edition=edition,
            signup_start__lt=date.today(),
            signup_end__gte=date.today(),
        )

    def csv_name(self):
        return '{}_{}'.format(
            self.event_start.strftime('%Y-%m-%d'),
            str(self.center).replace(' ', '_'),
        )

    def short_description(self):
        return '{} – {} to {}'.format(
            self.center.name,
            date_format(self.event_start, "SHORT_DATE_FORMAT"),
            date_format(self.event_end, "SHORT_DATE_FORMAT"),
        )

    def __str__(self):
        return '{}-{} {}'.format(
            self.event_start.strftime('%Y-%m-%d'),
            self.event_start.strftime('%Y-%m-%d'),
            self.center,
        )
