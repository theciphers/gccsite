# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

from django import template
from gcc.models import ApplicantStatusTypes as StatusType


register = template.Library()


def status_badge(status):
    """
    Get the bootstrap's badge class name that best represents the input status.
    """
    if status in [StatusType.pending.value]:
        return 'badge-default'
    if status in [StatusType.selected.value, StatusType.confirmed.value]:
        return 'badge-success'
    if status in [StatusType.incomplete.value, StatusType.accepted.value]:
        return 'badge-warning'
    if status in [StatusType.rejected.value]:
        return 'badge-danger'


register.filter('status_badge', status_badge)
