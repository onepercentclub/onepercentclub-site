import logging
logger = logging.getLogger(__name__)

from legacy.legacymembers.models import Profile
from apps.accounts.models import UserProfile

from .base import MigrateModel

from mappings import (
    CropMapping, EducateDateTimeMapping, SubstitutionMapping, Mapping,
    NoneToStringCroppingMapping
)


class MigrateProfile(MigrateModel):
    from_model = Profile
    to_model = UserProfile

    def get_to_correspondence(self, other_object):
        return {'user__pk': other_object.member.pk}

    def get_from_correspondence(self, other_object):
        return {'member__pk': other_object.user.pk}

    field_mapping = {
    }
