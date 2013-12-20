from django.contrib import messages, admin
from django.contrib.contenttypes.models import ContentType

from django.db import transaction

from django.conf.urls import url, patterns
from django.shortcuts import render

from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from django.http import HttpResponseRedirect

from .utils.admin import ExtendibleModelAdminMixin


class IncrementalCSVImportMixin(ExtendibleModelAdminMixin):
    """
    Admin mixin featuring incremental CSV imports through uploads.

    This admin requires a subclass of CSVImportForm the be specified as
    `import_form`. Example::

        class BankTransactionImportForm(CSVImportForm):
            # Map field names or numbers to database fields
            field_mapping = {
                0: 'sender_account',
                1: 'currency',
            }

        class BankTransactionAdmin(IncrementalCSVImportMixin, admin.ModelAdmin):
            form = BankTransactionImportForm

    """

    change_list_template = 'admin/csv_import/change_list.html'

    def get_urls(self):
        """ Add import view to URL's. """
        urls = super(IncrementalCSVImportMixin, self).get_urls()

        new_urls = patterns('',
            url(
                r'^import/$',
                self._wrap(self.import_view),
                name=self._view_name('import')
            )
        )

        return new_urls + urls

    def get_import_form(self):
        """ Return form used for imports. """

        return self.import_form

    @transaction.commit_on_success
    def import_view(self, request):
        """ Render or process import form. """

        import_form = self.get_import_form()

        if request.method == 'POST':
            # If the form has been submitted...

            # A form bound to the POST data
            form = import_form(request.POST, request.FILES, model=self.model)

            if form.is_valid():
                # All validation rules pass, attempt writing to the database

                # Save records to database
                (new_records, ignored_records) = form.save()

                # Success notification
                messages.success(
                    request, _(
                        '%d new records have been imported, '
                        '%d have been already imported and have been ignored.'
                    ) % (new_records, ignored_records)
                )

                # Redirect after POST
                return HttpResponseRedirect('../')

        else:
            # An unbound form
            form = import_form()

        # Most of the code below is copied from django.contrib.admin.options
        opts = self.model._meta

        adminForm = admin.helpers.AdminForm(
            form,
            fieldsets=[(None, {'fields': form.base_fields})],
            prepopulated_fields={}
        )

        templates = self.add_form_template or [
            "admin/%s/%s/change_form.html" % (
                opts.app_label, opts.object_name.lower()),
            "admin/%s/change_form.html" % opts.app_label,
            "admin/change_form.html"
        ]

        return render(
            request, templates, {
                'title': _('Import %s') % force_text(opts.verbose_name_plural),
                'adminform': adminForm,
                # 'media': media,
                # 'inline_admin_formsets': inline_admin_formsets,
                'errors': admin.helpers.AdminErrorList(form, []),
                'app_label': opts.app_label,

                'add': True,
                'change': False,
                'has_add_permission': False,
                'has_change_permission': False,
                'has_delete_permission': False,
                'has_file_field': True, # FIXME - this should check if form or formsets have a FileField,
                'has_absolute_url': False,
                # 'ordered_objects': ordered_objects,
                'form_url': '',
                'opts': opts,
                'content_type_id': ContentType.objects.get_for_model(self.model).id,
                'save_as': False,
                'save_on_top': False,
                'is_popup': False,
            }
        )
