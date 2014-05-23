from dateutil.relativedelta import relativedelta
from bluebottle.bb_projects.models import ProjectPhase

from django.utils import timezone

from .models import Payout
from .choices import PayoutLineStatuses


def create_payout_for_fully_funded_project(sender, instance, created, **kwargs):
    """ Create or update Payout for fully funded projects. """

    project = instance
    now = timezone.now()

    # Check projects in phase Act that have asked for money.
    # import ipdb; ipdb.set_trace()
    if project.status == ProjectPhase.objects.get(slug="done-complete") and \
                         project.money_asked:
        if now.day <= 15:
            next_date = timezone.datetime(now.year, now.month, 15)
        else:
            next_date = timezone.datetime(now.year, now.month, 1) + relativedelta(months=1)

        try:
            # Update existing Payout
            payout = Payout.objects.get(project=project)

            if payout.status == PayoutLineStatuses.new:
                # Update planned payout date for new Payouts
                # We *might* also want to call calculate_amounts() here.
                payout.planned = next_date
                payout.save()

        except Payout.DoesNotExist:

            # Create new Payout
            payout = Payout(
                planned=next_date,
                project=project
            )

            # Calculate amounts
            payout.calculate_amounts()

            # Set payment details
            organization = project.organization
            payout.receiver_account_bic = organization.account_bic
            payout.receiver_account_iban = organization.account_iban
            payout.receiver_account_number = organization.account_number
            payout.receiver_account_name = organization.account_name
            payout.receiver_account_city = organization.account_city
            payout.receiver_account_country = organization.account_bank_country

            # Generate invoice reference, saves twice
            payout.update_invoice_reference(auto_save=True)
