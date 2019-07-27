# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

from django.contrib import admin

from gcc.models.review import ReviewLabel


admin.site.register(ReviewLabel)
