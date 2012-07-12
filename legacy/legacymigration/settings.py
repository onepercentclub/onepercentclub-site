from .accounts import MigrateMemberAuth
from .profiles import MigrateProfile, MigrateUserAddress
from .projects import MigrateProject


MIGRATIONS = (
    MigrateMemberAuth,
    MigrateProfile,
    MigrateUserAddress,
    MigrateProject,
)
