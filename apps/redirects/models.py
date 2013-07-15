from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

class Redirect(models.Model):
    old_path = models.CharField(_('redirect from'), max_length=200, db_index=True, unique=True,
        help_text=_("This should be an absolute path, excluding the domain name. Example: '/events/search/'."))
    new_path = models.CharField(_('redirect to'), max_length=200, blank=True,
        help_text=_("This can be either an absolute path (as above) or a full URL starting with 'http://'."))
    regular_expression = models.BooleanField(_('Match using regular expressions'),
                                             default=False,
                                             help_text=_("If checked, the redirect-from and redirect-to fields will also be processed using regular expressions when matching incoming requests.<br>Example: <strong>/projects/.* -> /#!/projects</strong> will redirect everyone visiting a page starting with /projects/<br>Example: <strong>/projects/(.*) -> /#!/projects/$1</strong> will turn /projects/myproject into /#!/projects/myproject<br><br>Invalid regular expressions will be ignored."))

    fallback_redirect = models.BooleanField(_("Fallback redirect"),
                                            default=False,
                                            help_text=_("This redirect is only matched after all other redirects have failed to match.<br>This allows us to define a general 'catch-all' that is only used as a fallback after more specific redirects have been attempted."))

    nr_times_visited = models.IntegerField(default=0,
                                           help_text=_("Is incremented each time a visitor hits this redirect"))

    class Meta:
        verbose_name = _('redirect')
        verbose_name_plural = _('redirects')
        db_table = 'django_redirect'
        ordering = ('fallback_redirect', 'regular_expression', 'old_path',)

    def __str__(self):
        return "%s ---> %s" % (self.old_path, self.new_path)
