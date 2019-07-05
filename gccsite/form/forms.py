from django import forms

from application.models import Answer, Applicant
from form.models import AnswerTypes, QuestionForForm


def build_dynamic_form(form, user, edition):
    """Build a form with fields described in models.Question"""

    class DynamicForm(forms.Form):
        @staticmethod
        def question_field_name(question_id):
            return 'field_{}'.format(question_id)

        def __init__(self, *args, **kwargs):
            kwargs.pop('instance')
            super(DynamicForm, self).__init__(*args, **kwargs)

            self.edition = edition
            self.form = form

            # Add fields to the form, query directly on the jointure in order
            # to take the ordering into account
            self.questions = [
                joined.question
                for joined in QuestionForForm.objects.filter(form=form)
            ]

            for question in self.questions:
                # set basic fields parameters
                basic_args = {
                    'label': str(question),
                    'required': question.always_required,
                    'help_text': question.comment,
                }
                field_id = self.question_field_name(question.pk)

                # Try to load existing configuration
                try:
                    answer = Answer.objects.get(
                        question=question,
                        applicant__user=user,
                        applicant__edition=edition,
                    )
                    basic_args['initial'] = answer.response
                except Answer.DoesNotExist:
                    pass

                if question.response_type == AnswerTypes.boolean.value:
                    self.fields[field_id] = forms.BooleanField(**basic_args)
                elif question.response_type == AnswerTypes.integer.value:
                    self.fields[field_id] = forms.IntegerField(**basic_args)
                elif question.response_type == AnswerTypes.date.value:
                    self.fields[field_id] = forms.DateField(**basic_args)
                elif question.response_type == AnswerTypes.string.value:
                    self.fields[field_id] = forms.CharField(**basic_args)
                elif question.response_type == AnswerTypes.text.value:
                    self.fields[field_id] = forms.CharField(
                        widget=forms.Textarea, **basic_args
                    )
                elif question.response_type == AnswerTypes.multichoice.value:
                    self.fields[field_id] = forms.ChoiceField(
                        choices=[
                            (str(choice), question.meta['choices'][choice])
                            for choice in question.meta['choices'].keys()
                        ],
                        **basic_args,
                    )

        def save(self):
            """
            Saves all filled fields for the applicant defined by the user and
            edition specified in __init__.
            """
            data = self.cleaned_data
            applicant = Applicant.for_user_and_edition(user, self.edition)

            for question in self.questions:
                field_id = self.question_field_name(question.pk)

                if data[field_id] is not None:
                    # Try to modify existing answer, create a new answer if it
                    # doesn't exist
                    try:
                        answer = Answer.objects.get(
                            applicant=applicant, question=question
                        )
                    except Answer.DoesNotExist:
                        answer = Answer(applicant=applicant, question=question)

                    answer.response = data[field_id]
                    answer.save()

    return DynamicForm
