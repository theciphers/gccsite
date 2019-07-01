# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

from django import template
from django.urls import reverse, NoReverseMatch
import re

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    # TODO: fixme
    #  try:
    #      pattern = '^' + reverse(pattern_or_urlname)
    #  except NoReverseMatch:
    #      pattern = pattern_or_urlname
    #  path = context['request'].path
    #  if re.search(pattern, path):
    #      return 'active'
    return ''


@register.simple_tag(takes_context=True)
def url_args_replace(context, field, value):
    get = context['request'].GET.copy()
    get[field] = value
    return get.urlencode()
