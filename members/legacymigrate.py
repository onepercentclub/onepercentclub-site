from django.contrib.auth.models import User

from members.models import Member


class MigrateModel(object):
    """
    Generic migration class, from one model class to another.
    """

    def copy_fields(self, from_instance, to_instance):
        """ Copy all fields from one object to another. """

        for field in self.copy_fields:
            value = getattr(from_instance, field)
            setattr(to_instance, field, value)

    def list_from(self):
        """ Return an iterable with all objects to be mapped to the new model. """

        # Default is to return all objects
        return self.from_model.objects.all()

    def get_to(self, from_instance):
        """
        Given an existing 'old' instance, return the corresponding 'new'
        instance or None if no corresponding object exists.
        """
        # Default is to look up by id
        try:
            return self.to_model.objects.get(pk=from_instance.pk)

        except self.to_model.DoesNotExist:
            return None

    def migrate_single(self, from_instance, to_instance):
        """ Migrate a single object. """
        self.copy_fields(from_instance, to_instance)

    def migrate_all(self):
        """ Migrate all the stuff. """

        for from_instance in self.list_from():
            to_instance = self.get_to(from_instance)

            self.migrate_single(from_instance, to_instance)

            to_instance.save()


class MigrateMemberAuth(MigrateModel):
    from_model = Member
    to_model = User
    copy_fields = ('id', 'email')
