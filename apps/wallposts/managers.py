from apps.bluebottle_utils.managers import GenericForeignKeyManagerMixin
from django.db import models
from polymorphic import PolymorphicManager


class WallPostManager(GenericForeignKeyManagerMixin, PolymorphicManager):
    pass


class ReactionManager(models.Manager):
    def get_query_set(self):
        queryset = super(ReactionManager, self).get_query_set()
        return queryset.filter(deleted__isnull=True)
