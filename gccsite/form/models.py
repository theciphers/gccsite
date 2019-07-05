from adminsortable.models import SortableMixin
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from prologin.utils import ChoiceEnum
from prologin.models import EnumField


@ChoiceEnum.labels(str.capitalize)
class AnswerTypes(ChoiceEnum):
    boolean = 0
    integer = 1
    date = 2
    string = 3
    text = 4
    multichoice = 5


class Form(models.Model):
    # Name of the form
    name = models.CharField(max_length=64)
    # List of question
    question_list = models.ManyToManyField(
        'Question', through='QuestionForForm'
    )

    def __str__(self):
        return self.name


class Question(models.Model):
    """
    A generic question type, that can be of several type.

    If response_type is multichoice you have to specify the answer in the meta
    field, respecting the following structure:
    {
        "choices": {
            "0": "first option",
            "1": "second option"
        }
    }
    """

    # Formulation of the question
    question = models.TextField()
    # Potential additional indications about the questions
    comment = models.TextField(blank=True)
    # How to represent the answer
    response_type = EnumField(AnswerTypes)

    # If set to true, the applicant will need to fill this field in order to
    # save his application.
    always_required = models.BooleanField(default=False)
    # If set to true, the applicant will need to fill this field in order to
    # validate his application.
    finaly_required = models.BooleanField(default=True)

    # Some extra constraints on the answer
    meta = JSONField(encoder=DjangoJSONEncoder, default=dict, null=True)

    def __str__(self):
        ret = self.question

        if self.finaly_required:
            ret += ' (*)'

        return ret


class QuestionForForm(SortableMixin):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(
        default=0, editable=False, db_index=True
    )

    class Meta:
        ordering = ['order']
