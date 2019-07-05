from django.contrib.auth import get_user_model
from django.db import models

from event.models import Event


class ApplicantLabel(models.Model):
    """
    Labels are used to add custom comments on an applicant.

    They are purposingly designed to be less volatile to use than comments in
    order to make sure that no RGPD-unsafe data is attached to a profile.
    """

    display = models.CharField(max_length=10)

    def __str__(self):
        return self.display


class Corrector(models.Model):
    """
    List of correctors allowed to review an event
    """

    db_table = 'migration_corrector'

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='correctors'
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='migrate_corrector_user',
    )

    def __str__(self):
        return str(self.user)
