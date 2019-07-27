# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

from django import template
from gcc.models.applicant import StatusTypes


register = template.Library()


def status_badge(status):
    """
    Get the bootstrap's badge class name that best represents the input status.
    """
    if status in [StatusTypes.pending.value]:
        return 'badge-default'
    if status in [StatusTypes.selected.value, StatusTypes.confirmed.value]:
        return 'badge-success'
    if status in [StatusTypes.incomplete.value, StatusTypes.accepted.value]:
        return 'badge-warning'
    if status in [StatusTypes.rejected.value]:
        return 'badge-danger'


register.filter('status_badge', status_badge)
