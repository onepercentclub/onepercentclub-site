import logging
logger = logging.getLogger(__name__)

from legacy.legacydonations.models import (
    Donation as LegacyDonation,
    DonationLine as LegacyDonationLine
)

from apps.donations.models import Donation, DonationLine

from .base import MigrateModel

from .projects import MigrateProject
from .accounts import MigrateMemberAuth

from .mappings import (
    EducateDateTimeMapping, StringToDecimalMapping, MappingMapping
)


class MigrateDonation(MigrateModel):
    from_model = LegacyDonation
    to_model = Donation

    def list_from(self):
        """
        Only migrate donations for migrated members.
        """

        qs = super(MigrateDonation, self).list_from()

        m = MigrateMemberAuth()
        member_list = m.list_from()

        # Only migrate profiles for migrated members
        qs = qs.filter(member__in=member_list)

        return qs


    field_mapping = {
        # ID's do not correspond for profiles
        'id': True,

        'member': None,
        'member_id': 'user_id',

        'amount': StringToDecimalMapping(verbose=False),

        'created': EducateDateTimeMapping(verbose=False),

        'status': MappingMapping({
            'closed': Donation.DonationStatuses.closed,
            'expired': Donation.DonationStatuses.expired,
            'paid': Donation.DonationStatuses.paid,
            'canceled': Donation.DonationStatuses.canceled,
            'chargedback': Donation.DonationStatuses.chargedback,
            'new': Donation.DonationStatuses.new,
            'started': Donation.DonationStatuses.started,
        }, verbose=False),

        'automatic_donation': None,
        'changed_to_safe': None,
        'donationline': None,
        'external': None,
        'meta_considered_safe': None,
        'payment_cluster': None,
        'projects': None,
        'thanks': None,
        'type': None,
        'voucher': None
    }


class MigrateDonationLine(MigrateModel):
    from_model = LegacyDonationLine
    to_model = DonationLine

    def list_from(self):
        """
        Only migrate donationlines for migrated donations and migrated
        projects.
        """

        qs = super(MigrateDonationLine, self).list_from()

        m = MigrateDonation()
        donation_list = m.list_from()

        m = MigrateProject()
        project_list = m.list_from()

        # Only migrate profiles for migrated members
        qs = qs.filter(donation__in=donation_list, project__in=project_list)

        return qs

    field_mapping = {
        'id': True,

        'donation': None,
        'donation_id': True,

        'project': None,
        'project_id': True,

        'amount': StringToDecimalMapping(verbose=False),

        'settlementline': None

    }