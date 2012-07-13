from .accounts import MigrateMemberAuth
from .profiles import MigrateProfile, MigrateUserAddress
from .organizations import MigrateOrganization, MigrateOrganizationMember
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
    MigrateOrganizationMember,
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
