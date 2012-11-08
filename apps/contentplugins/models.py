"""
ContentItem models for custom django-fluent-contents plugins.
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djchoices import DjangoChoices, ChoiceItem
from fluent_contents.models import ContentItem
from sorl.thumbnail import ImageField


class PictureItem(ContentItem):
    """
    Picture content item
    """
    class PictureAlignment(DjangoChoices):
        float_left = ChoiceItem('float-left', label=_("Float left"))
        center = ChoiceItem('center', label=_("Center"))
        float_right = ChoiceItem('float-right', label=_("Float right"))

    image = ImageField(_("Picture"), upload_to='content_images')
    align = models.CharField(_("Align"), max_length=50, choices=PictureAlignment.choices)

    class Meta:
        verbose_name = _("Picture")
        verbose_name_plural = _("Pictures")

    def __unicode__(self):
        return self.image.name if self.image else u'(no image)'
