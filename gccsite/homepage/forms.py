from django import forms
from django.utils.translation import ugettext_lazy as _


class EmailForm(forms.Form):
    # See here for why 254 max
    # http://www.rfc-editor.org/errata_search.php?rfc=3696&eid=1690
    email = forms.EmailField(label=_('Email address'), max_length=254)
