# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

from collections import OrderedDict

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Q

from prologin.models import EnumField
from prologin.utils import ChoiceEnum

from .edition import Edition, Event
from .forms import AnswerTypes, Question
from .review import ApplicantLabel


@ChoiceEnum.labels(str.capitalize)
class ApplicantStatusTypes(ChoiceEnum):
    incomplete = 0  # the candidate hasn't finished her registration yet
    pending = 1  # the candidate finished her registration
    rejected = 2  # the candidate's application has been rejected
    selected = 3  # the candidate has been selected for participation
    accepted = 4  # the candidate has been assigned to an event and emailed
    confirmed = 5  # the candidate confirmed her participation


# Increasing order of status, for example, if the wishes of a candidate have
# separate status, the greatest one is displayed
STATUS_ORDER = [
    ApplicantStatusTypes.rejected.value,
    ApplicantStatusTypes.incomplete.value,
    ApplicantStatusTypes.pending.value,
    ApplicantStatusTypes.selected.value,
    ApplicantStatusTypes.accepted.value,
    ApplicantStatusTypes.confirmed.value,
]


class Applicant(models.Model):
    """
    An applicant for a specific edition and reviews about him.

    Notice that no free writing field has been added yet in order to ensure an
    GDPR-safe usage of reviews.
    """

    # General informations about the application
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    edition = models.ForeignKey(Edition, on_delete=models.CASCADE)

    # Wishes of the candidate
    # TODO: Rename as assignation_event is deprecated
    assignation_wishes = models.ManyToManyField(
        Event, through='EventWish', related_name='applicants', blank=True
    )

    # Wishes she is accepted to
    # TODO: Deprecated (use wish-specific status)
    assignation_event = models.ManyToManyField(
        Event, related_name='assigned_applicants', blank=True
    )

    # Review of the application
    labels = models.ManyToManyField(ApplicantLabel, blank=True)

    @property
    def status(self):
        wishes_status = set(wish.status for wish in self.eventwish_set.all())

        for wish_status in reversed(STATUS_ORDER):
            if wish_status in wishes_status:
                return wish_status

        return ApplicantStatusTypes.incomplete.value

    def is_locked(self):
        return EventWish.objects.filter(
            ~Q(
                status__in=[
                    ApplicantStatusTypes.incomplete.value,
                    ApplicantStatusTypes.rejected.value,
                ]
            ),
            applicant=self,
        ).exists()

    def has_rejected_choices(self):
        return EventWish.objects.filter(
            applicant=self, status=ApplicantStatusTypes.rejected.value
        ).exists()

    def has_non_rejected_choices(self):
        return EventWish.objects.filter(
            ~Q(status=ApplicantStatusTypes.rejected.value), applicant=self
        ).exists()

    def get_export_data(self):
        """
        Return an array of data to be converted to csv
        """

        export_datas = OrderedDict()
        export_datas["Username"] = self.user.username
        export_datas["First name"] = self.user.first_name
        export_datas["Last name"] = self.user.last_name
        export_datas["Email"] = self.user.email
        export_datas["Edition"] = str(self.edition)
        export_datas["Labels"] = str(self.labels)

        questions = self.edition.signup_form.question_list.all()

        for question in questions:
            try:
                answer = Answer.objects.get(applicant=self, question=question)
                export_datas[str(question)] = str(answer)
            except Answer.DoesNotExist:
                export_datas[str(question)] = "(empty)"

        return export_datas

    def get_status_display(self):
        return ApplicantStatusTypes(self.status).name

    def list_of_assignation_wishes(self):
        return [event for event in self.assignation_wishes.all()]

    def list_of_assignation_event(self):
        return [event for event in self.assignation_event.all()]

    def has_complete_application(self):
        # TODO: optimize requests
        if not self.user.has_complete_profile():
            return False

        questions = Edition.current().signup_form.question_list.all()
        for question in questions:
            try:
                answer = Answer.objects.get(applicant=self, question=question)
                if not answer.is_valid():
                    return False
            except Answer.DoesNotExist:
                return question.finaly_required

        return True

    def validate_current_wishes(self):
        for wish in self.eventwish_set.all():
            if wish.status == ApplicantStatusTypes.incomplete.value:
                wish.status = ApplicantStatusTypes.pending.value
                wish.save()

    @staticmethod
    def incomplete_applicants_for(event):
        """
        List the applicants which are incomplete.
        """
        acceptable_wishes = EventWish.objects.filter(
            event=event, status=ApplicantStatusTypes.incomplete.value
        )
        return [wish.applicant for wish in acceptable_wishes]

    @staticmethod
    def acceptable_applicants_for(event):
        """
        List the applicants which are waiting to be accepted (ie. in the state
        `selected`).
        """
        acceptable_wishes = EventWish.objects.filter(
            event=event, status=ApplicantStatusTypes.selected.value
        )
        return [wish.applicant for wish in acceptable_wishes]

    @staticmethod
    def accepted_applicants_for(event):
        """
        List the applicants which are accepted but did not confirm.
        """
        accepted_wishes = EventWish.objects.filter(
            event=event, status=ApplicantStatusTypes.accepted.value
        )
        return [wish.applicant for wish in accepted_wishes]

    @staticmethod
    def confirmed_applicants_for(event):
        """
        List the applicants which are confirmed.
        """
        confirmed_wishes = EventWish.objects.filter(
            event=event, status=ApplicantStatusTypes.confirmed.value
        )
        return [wish.applicant for wish in confirmed_wishes]

    @staticmethod
    def rejected_applicants_for(event):
        """
        List the applicants which were rejected.
        """
        acceptable_wishes = EventWish.objects.filter(
            event=event, status=ApplicantStatusTypes.rejected.value
        )
        return [wish.applicant for wish in acceptable_wishes]

    @staticmethod
    def for_user_and_edition(user, edition):
        """
        Get applicant object corresponding to an user for given edition. If no
        applicant has been created for this edition yet, it will be created.
        """
        applicant, created = Applicant.objects.get_or_create(
            user=user, edition=edition
        )

        if created:
            applicant.save()

        return applicant

    def __str__(self):
        return str(self.user) + '@' + str(self.edition)

    class AlreadyLocked(Exception):
        """
        This exception is raised if a new application is submitted for an user
        who has already been accepted or rejected this year.
        """

    class Meta:
        unique_together = (('user', 'edition'),)


class Answer(models.Model):
    applicant = models.ForeignKey(
        Applicant, related_name='answers', on_delete=models.CASCADE
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = JSONField(encoder=DjangoJSONEncoder)

    def is_valid(self):
        '''
        Check if an answer is valid, a checkbox with required beeing true must
        be checked, and other kind of fields must necessary be filled.
        '''
        if not self.question.finaly_required:
            return True

        return bool(self.response)

    def __str__(self):
        if self.question.response_type == AnswerTypes.multichoice.value:
            if str(self.response) not in self.question.meta['choices']:
                return ''

            return self.question.meta['choices'][str(self.response)]

        return str(self.response)

    class Meta:
        unique_together = (('applicant', 'question'),)


class EventWish(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = EnumField(
        ApplicantStatusTypes,
        db_index=True,
        blank=True,
        default=ApplicantStatusTypes.incomplete.value,
    )

    # Priority defined by the candidate to express his preferred event
    # The lower the order is, the more important is the choice
    order = models.IntegerField(default=1)

    def __str__(self):
        return '{} for {}'.format(str(self.applicant), str(self.event))

    class Meta:
        ordering = ('order',)
        unique_together = (('applicant', 'event'),)
