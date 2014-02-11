from bluebottle.utils.managers import GenericForeignKeyManagerMixin
from django.db import models
from polymorphic import PolymorphicManager


class WallPostManager(GenericForeignKeyManagerMixin, PolymorphicManager):
    def get_query_set(self):
        queryset = super(WallPostManager, self).get_query_set()
        return queryset.filter(deleted__isnull=True)


class ReactionManager(models.Manager):
    def get_query_set(self):
        queryset = super(ReactionManager, self).get_query_set()
        return queryset.filter(deleted__isnull=True)
