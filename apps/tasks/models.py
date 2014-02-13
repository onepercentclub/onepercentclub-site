from django.db import models
from bluebottle.bb_tasks.models import BaseTask
from django.utils.translation import ugettext as _


class Task(BaseTask):
    """
    Extended Task model for 1%Club
    """
    end_goal = models.TextField(_("end goal"))
    location = models.CharField(_("location"), max_length=200)

    expertise = models.CharField(_("old expertise"), max_length=200)

    people_needed = models.PositiveIntegerField(
        _("people needed"), default=1,
        help_text=_("How many people are needed for this task?"))

