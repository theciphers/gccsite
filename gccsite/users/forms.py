from crispy_forms import layout
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm as DjangoAuthenticationForm
from django.utils.safestring import mark_safe

from prologin.models import Gender
from prologin.utils import _
from prologin.utils.forms import ConfirmDangerMixin

User = get_user_model()


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            # left column
            'first_name', 'last_name', 'gender', 'email', 'birthday',
            'address', 'postal_code', 'city', 'country',
            'phone', 'school_stage',
            # right column
            'gender', 'allow_mailing', 'timezone',
            'preferred_locale')
        widgets = {
            'gender': forms.RadioSelect(),
            'address': forms.Textarea(attrs=dict(rows=2)),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['gender'].required = False
        self.fields['gender'].label = _("How do you prefer to be described?")
        self.fields['gender'].choices = [
            (Gender.female.value, mark_safe(_("<em>She is writing code for the contest</em>"))),
            (Gender.male.value, mark_safe(_("<em>He is writing code for the contest</em>"))),
            ("", _("Other or prefer not to tell")),
        ]

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        # input, input, ...
        self.helper[:6].wrap_together(layout.Div, css_class="col-md-6")
        # COL, input, input...
        self.helper[1:].wrap_together(layout.Div, css_class="col-md-6")
        # COL, COL
        self.helper[:].wrap_together(layout.Div, css_class="row")

    def clean(self):
        return super().clean()


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254, required=True,
                             widget=forms.EmailInput(attrs={'placeholder': _("Your email address")}))


class AuthenticationForm(DjangoAuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _("Username or email")
        self.fields['username'].help_text = _("This field is case insensitive. It means capitals and small letters are "
                                              "considered to be equal.")
        self.error_messages['invalid_login'] = _("Please enter a correct username (or email) and password.")


class ConfirmDeleteUserForm(ConfirmDangerMixin, forms.ModelForm):
    username_conf = forms.CharField(
        required=True, label=_("Your username"),
        help_text=_("Type your username to confirm you know what you are doing."))

    class Meta:
        model = get_user_model()
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.instance
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout('username_conf', 'password_conf')
        self.fields['username_conf'].widget.attrs['placeholder'] = self.instance.username
        # https://bugs.chromium.org/p/chromium/issues/detail?id=468153
        self.fields['username_conf'].widget.attrs['autocomplete'] = 'new-username'
        self.fields['password_conf'].widget.attrs['autocomplete'] = 'new-password'

    def clean_username_conf(self):
        if self.cleaned_data['username_conf'] != self.instance.username:
            raise forms.ValidationError(_("Wrong username."))
