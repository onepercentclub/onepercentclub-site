from django.db import models
from bluebottle.bb_tasks.models import BaseTask, BaseSkill, BaseTaskFile, BaseTaskMember
from django.utils.translation import ugettext as _


class Task(BaseTask):
    """
    Extended Task model for 1%Club
    """
    pass


class Skill(BaseSkill):
    pass


class TaskMember(BaseTaskMember):
    pass


class TaskFile(BaseTaskFile):
    pass
