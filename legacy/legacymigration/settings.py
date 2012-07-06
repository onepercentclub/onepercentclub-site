from .accounts import MigrateMemberAuth
from .profiles import MigrateProfile

MIGRATIONS = (
    MigrateMemberAuth,
    MigrateProfile
)
