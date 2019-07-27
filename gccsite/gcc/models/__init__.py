# Copyright (C) <2019> Association Prologin <association@prologin.org>
# SPDX-License-Identifier: GPL-3.0+

from .applicant import Applicant, Answer, EventWish
from .edition import Edition, Event
from .forms import Form, Question, QuestionForForm
from .newsletter import SubscriberEmail
from .review import Corrector
from .sponsor import Sponsor

# TODO: import from real path and rename
from .review import ApplicantLabel
