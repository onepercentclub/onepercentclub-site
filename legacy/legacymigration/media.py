import logging
logger = logging.getLogger(__name__)

import settings

from django.db.models import Q

from legacy.legacyprojects.models import Video as LegacyVideo
from legacy.legacyalbums.models import (
    Catalog as LegacyCatalog,
    Album as LegacyAlbum,
    Picture as LegacyPicture
)

from apps.media.models import Album, EmbeddedVideo, LocalPicture
from apps.projects.models import Project

from .base import MigrateModel

from .projects import MigrateProject

from .mappings import (
    IdentityMapping, EducateDateTimeMapping, OneToManyMapping,
    SlugifyCroppingMapping, PathToFileMapping
)


class ProjectToAlbumMapping(IdentityMapping):
    """ Map a project to an album with the same slug. """

    def map_value(self, old_value):
        project = Project.objects.get(pk=old_value.pk)

        # Either create or find a 'default' album for a project by
        # project slug
        (album, created) = Album.objects.get_or_create(
            slug=project.slug
        )

        # If created, set title
        if created:
            album.title=project.title
            album.save()

        return album


class IgnorantSlugifyCroppingMapping(SlugifyCroppingMapping):
    """ Ignore changes to original slug in order to make unique. """

    def check(self, from_instance, to_instance, from_field):
        if not super(IgnorantSlugifyCroppingMapping, self).check(
            from_instance, to_instance, from_field
        ):
            old_value = getattr(from_instance, from_field)
            mapped_value = self.map_value(old_value)

            new_value = getattr(to_instance, self.get_to_field(from_field))

            logger.warning('Field %s has been renamed on %s',
                from_field, to_instance
            )

            if not mapped_value+'-' in new_value:
                logger.error('Wowowoww')
                return False

        return True


class MigrateAlbum(MigrateModel):
    from_model = LegacyAlbum
    to_model = Album

    def list_from(self):
        qs = super(MigrateAlbum, self).list_from()

        m = MigrateProject()
        project_list = m.list_from()

        # Only migrate albums for migrated projects
        qs = qs.filter(catalog__project__in=project_list)

        # This ignores about 6 albums
        qs = qs.exclude(Q(name='*') | Q(name='.'))

        return qs

    def migrate_single(self, from_instance, to_instance):
        super(MigrateAlbum, self).migrate_single(
            from_instance,
            to_instance
        )

        # Check whether this username already exists. If so, add a number
        counter = 1

        # Detect and change duplicate usernames
        qs = self.list_to().exclude(pk=to_instance.pk)

        original_slug = to_instance.slug

        while qs.filter(slug=to_instance.slug).exists():
            to_instance.slug = '%s-%d' % (original_slug, counter)

            logger.warn('Duplicate slug %s, changing to %s',
                original_slug, to_instance.slug
            )

            counter += 1


    field_mapping = {
        'id': True,
        'name': OneToManyMapping(
            IdentityMapping('title'),
            IgnorantSlugifyCroppingMapping(
                100, to_field='slug', verbose=False)
        ),
        'description': True,

        'created': EducateDateTimeMapping(verbose=False),
        #'updated': EducateDateTimeMapping(verbose=False),

        'folder': None,
    }


class MigratePicture(MigrateModel):
    from_model = LegacyPicture
    to_model = LocalPicture

    def list_from(self):
        qs = super(MigratePicture, self).list_from()

        m = MigrateAlbum()
        album_list = m.list_from()

        # Only migrate albums for migrated projects
        qs = qs.filter(album__in=album_list)

        return qs

    field_mapping = {
        'id': True,
        'album': None,
        'album_id': True,
        'name': 'title',
        'description': True,
        'created': EducateDateTimeMapping(verbose=False),
        #'updated': EducateDateTimeMapping(verbose=False),

        # For now, only migrate pictures related to albums
        # Note: in the source database, an album is required
        'project': None,

        'file': {
            'file':
                PathToFileMapping(
                    root_path=settings.LEGACY_MEDIA_ROOT + '/assets/files/filemanager',
                    allow_missing=True,
                    to_field='picture',
                    verbose=False
                ),
        }

    }


class MigrateVideo(MigrateModel):
    from_model = LegacyVideo
    to_model = EmbeddedVideo

    def list_from(self):
        qs = super(MigrateVideo, self).list_from()

        m = MigrateProject()
        project_list = m.list_from()
        qs = qs.filter(project__in=project_list)

        return qs

    field_mapping = {
        'id': True,

        'url': None,
        'created': EducateDateTimeMapping(verbose=False),
        'name': 'title',
        'project': ProjectToAlbumMapping('album', verbose=False),

        # This will all be automatic now
        'thumb': None,
        'watch_url': 'url'
    }
