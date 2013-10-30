from django import forms
from django.contrib.admin.widgets import AdminFileWidget
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe


from .models import Organization, OrganizationDocument

# WIDGETS #############################################
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

class PrivateUrlFileInput(AdminFileWidget):
    """ 
    Class to allow private file downloads, changing the url to a view serving
    the file.
    """
    
    is_required = False
    
    def render(self, name, value, attrs=None):
        """ Override render to modify the download url """
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = '%(input)s'
        substitutions['input'] = super(forms.ClearableFileInput, self).render(name, value, attrs)

        if value and hasattr(value, "url"):
            url = reverse('organization-registration-download', kwargs={'pk': self.instance.id})
            template = self.template_with_initial
            substitutions['initial'] = format_html('<a href="{0}">{1}</a>',
                                                   url,
                                                   force_text(value))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = forms.CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)


# FORMS ###############################################
class OrganizationDocumentForm(forms.ModelForm):
    class Meta:
        model = OrganizationDocument
        widgets = {
            'file': UploadWidget()
        }

    def __init__(self, *args, **kwargs):
        super(OrganizationDocumentForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = False

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        widgets = {
            'registration': PrivateUrlFileInput()
        }

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.fields['registration'].widget.instance = self.instance
