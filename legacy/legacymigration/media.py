import logging
logger = logging.getLogger(__name__)

import settings

from django.db.models import Q

from legacy.legacyprojects.models import Video as LegacyVideo
from legacy.legacyalbums.models import (
    Album as LegacyAlbum,
    Picture as LegacyPicture
)

from apps.media.models import Album, EmbeddedVideo, LocalPicture
from apps.projects.models import Project

from .base import MigrateModel, UniqueSlugMixin

from .projects import MigrateProject

from .mappings import (
    IdentityMapping, EducateDateTimeMapping, OneToManyMapping,
    TolerantSlugifyCroppingMapping, PathToFileMapping
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

            project.albums.add(album)

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('Created album %s for project %s',
                    repr(album), repr(project)
                )

        return album

    def check_value(self, old_value, new_value):
        """ Check whether the album is related to the project. """

        result = super(ProjectToAlbumMapping, self).check_value(
            old_value, new_value
        )

        album = new_value

        if result:
            if album.project_set.filter(pk=old_value.pk).exists():
                return True
            else:
                logger.error(
                    'Album %s should be related to project %s but is '
                    'related to %s instead.',
                    repr(album), repr(old_value),
                    repr(album.project_set.all())
                )

                import ipdb; ipdb.set_trace()

        return False


class MigrateAlbum(UniqueSlugMixin, MigrateModel):
    """
    Migrate albums from old website to new.

    TODO: there's a known issue here where migrating albums *again*
    *after* video's have been migrated causes correspondence errors due
    to the fact that new albums get created during migration of the videos.

    We should figure out some way to mark the created albums differently
    and thus filter them from the destination queryset *or* simply
    disable the correspondence check.

    For now, use the following SQL to clean things up again::

        TRUNCATE TABLE "media_album" CASCADE;

    This will clear out the following tables:

      * "projects_project_albums"
      * "media_localpicture"
      * "media_embeddedvideo"

    """
    from_model = LegacyAlbum
    to_model = Album

    def _migrate_from(self, from_instance):
        """ Explicitly associate the migrated album with projects. """
        to_instance = super(MigrateAlbum, self)._migrate_from(from_instance)

        if from_instance.catalog:
            for project in from_instance.catalog.project_set.all():
                new_project = Project.objects.get(pk=project.pk)
                to_instance.project_set.add(new_project)

    def list_from(self):
        qs = super(MigrateAlbum, self).list_from()

        m = MigrateProject()
        project_list = m.list_from()

        # Only migrate albums for migrated projects
        qs = qs.filter(catalog__project__in=project_list)

        # This ignores about 6 albums
        qs = qs.exclude(Q(name='*') | Q(name='.'))

        # Exclude albums without pictures
        qs = qs.exclude(picture=None)

        return qs

    field_mapping = {
        'id': True,
        'name': OneToManyMapping(
            IdentityMapping('title'),
            TolerantSlugifyCroppingMapping(
                100, to_field='slug', verbose=False)
        ),
        'description': True,

        'created': EducateDateTimeMapping(verbose=False),
        #'updated': EducateDateTimeMapping(verbose=False),

        # Not migrated
        'folder': None,

        # Left out, albums relate to projects now directly
        'catalog': None
    }


class MigratePicture(MigrateModel):
    from_model = LegacyPicture
    to_model = LocalPicture

    def list_from(self):
        qs = super(MigratePicture, self).list_from()

        # Only migrate pictures for migrated albums
        m = MigrateAlbum()
        album_list = m.list_from()

        qs = qs.filter(album__in=album_list)

        # Exclude pictures that have no file set
        qs = qs.exclude(Q(file=None) | Q(file__file=None))

        return qs

    field_mapping = {
        'id': True,
        'album': None,
        'album_id': True,
        'name': 'title',
        'description': True,
        'created': EducateDateTimeMapping(verbose=False),
        #'updated': EducateDateTimeMapping(verbose=False),

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

        # Don't migrate videos for which no project has been set
        qs = qs.exclude(project=None)

        # Don't migrate video's for projects we're not migrating
        m = MigrateProject()
        project_list = m.list_from()
        qs = qs.filter(project__in=project_list)

        # This particular video is associated with an album that yields
        # a duplicate slug - for now: skip it!
        #
        # Orig. error: Album <Album: TOILETTEN> should be related to project
        # <Project: Toiletten voor de Sundayschool> but is related to
        # [<Project: Train de Trainer: Seksuele gezondheid>] instead
        #
        # We need to change the slug for the 'toiletten' album on
        # Train de Trainer OR prefix the albums with the project slug.
        qs = qs.exclude(pk=381)

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
