from .accounts import MigrateMemberAuth
from .profiles import MigrateProfile, MigrateUserAddress
from .organizations import MigrateOrganization
from .projects import MigrateProject

MIGRATIONS = (
    MigrateMemberAuth,
    MigrateProfile,
    MigrateUserAddress,
    MigrateOrganization,
    MigrateProject,
)
