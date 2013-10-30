from django import forms
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from django.utils.html import format_html

from .models import OrganizationDocument


class UploadWidget(forms.FileInput):
    def render(self, name, value, attrs=None):
        html = super(UploadWidget, self).render(name, value, attrs)
        if value:
            text = _('Change:')
        else:
            text = _('Add:')
        
        html = format_html(
            '<p class="url">{0} {1}</p>',
            text, html
        )
        return html

class OrganizationDocumentForm(forms.ModelForm):
    class Meta:
        model = OrganizationDocument
        widgets = {
            'file': UploadWidget()
        }

    def __init__(self, *args, **kwargs):
        super(OrganizationDocumentForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = False