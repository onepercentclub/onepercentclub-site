"""
The manager class for the blog models
"""
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.utils.timezone import now


class BlogPostQuerySet(QuerySet):
    def published(self):
        """
        Return only published entries
        """
        from .models import BlogPost # the import can't be globally, that gives a circular dependency
        qs = self
        qs = qs.filter(status=BlogPost.PostStatus.published)
        qs = qs.filter(Q(publication_date__isnull=True) | Q(publication_date__lte=now()))
        qs = qs.filter(Q(publication_end_date__isnull=True) | Q(publication_end_date__gte=now()))
        return qs


class BlogPostManager(models.Manager):
    """
    Extra methods attached to ``BlogPost.objects`` .
    """
    def get_query_set(self):
        return BlogPostQuerySet(self.model, using=self._db)

    def published(self):
        """
        Return only published entries
        """
        return self.get_query_set().published()


class BlogPostProxyManager(BlogPostManager):
    """
    Limit a Blog post proxy model to a specific subset.
    """
    def get_query_set(self):
        return super(BlogPostProxyManager, self).get_query_set().filter(post_type=self.model.limit_to_post_type)


    def create(self, **kwargs):
        kwargs.setdefault('post_type', self.model.limit_to_post_type)
        super(BlogPostProxyManager, self).create(**kwargs)
