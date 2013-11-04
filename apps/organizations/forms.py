from django import forms
from django.contrib.admin.widgets import AdminFileWidget
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

from .models import Organization, OrganizationDocument

# Widgets
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


# Forms
class OrganizationDocumentForm(forms.ModelForm):
    class Meta:
        model = OrganizationDocument
        widgets = {
            'file': UploadWidget()
        }

    def __init__(self, *args, **kwargs):
        super(OrganizationDocumentForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = False
