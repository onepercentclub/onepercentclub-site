from .accounts import MigrateMemberAuth
from .profiles import MigrateProfile, MigrateUserAddress
from .organizations import MigrateOrganization
from .projects import (
    MigrateProject, MigrateIdea, MigratePlan, MigrateAct, MigrateResults,
    MigrateLink, MigrateTestimonial, MigrateMessage, MigrateBudgetCategory,
    MigrateBudgetLine
)

MIGRATIONS = (
    MigrateMemberAuth,
    MigrateProfile,
    MigrateUserAddress,
    MigrateOrganization,
    MigrateProject,
    MigrateIdea,
    MigratePlan,
    MigrateAct,
    MigrateResults,
    MigrateLink,
    MigrateTestimonial,
    MigrateMessage,
    MigrateBudgetCategory,
    MigrateBudgetLine
)
