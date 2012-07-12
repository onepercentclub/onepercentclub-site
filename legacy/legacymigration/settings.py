from .accounts import MigrateMemberAuth
from .profiles import MigrateProfile, MigrateUserAddress


MIGRATIONS = (
    MigrateMemberAuth,
    MigrateProfile,
    MigrateUserAddress
)
