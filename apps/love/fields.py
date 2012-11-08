from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.functional import lazy


class LoveDeclarationRelation(GenericRelation):
    """
    A :class:`~django.contrib.contenttypes.generic.GenericRelation` which can be applied to a parent model that
    can be loved by a :class:`apps.love.models.LoveMarker` model. For example:

    .. code-block:: python

        class Comment(models.Model):
            received_loves = LoveDeclarationRelation()
    """
    def __init__(self, **kwargs):
        from .models import LoveDeclaration
        defaults = {
            'limit_choices_to': Q(
                parent_type=lazy(lambda: ContentType.objects.get_for_model(LoveDeclaration), ContentType)()
            )
        }
        defaults.update(kwargs)
        super(LoveDeclarationRelation, self).__init__(
            to=LoveDeclaration,
            object_id_field='object_id',
            content_type_field='content_type',
            **defaults
        )



try:
    from south.modelsinspector import add_ignored_fields
except ImportError:
    pass
else:
    # South 0.7.x ignores GenericRelation fields but doesn't ignore subclasses.
    # Adding them to the ignore list.
    _name_re = "^" + __name__.replace(".", "\.")
    add_ignored_fields((
        _name_re + "\.LoveDeclarationRelation",
    ))
