import csv
from decimal import Decimal
import math
import logging
import traceback
import sys
from collections import namedtuple
from optparse import make_option
from apps.donations.models import MonthlyDonation, MonthlyOrder, MonthlyBatch
from bluebottle.bb_projects.models import ProjectPhase
from django.utils.timezone import now

import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.cowry_docdata.adapters import WebDirectDocDataDirectDebitPaymentAdapter
from apps.cowry_docdata.exceptions import DocDataPaymentException
from apps.cowry_docdata.models import DocDataPaymentOrder
from apps.fund.models import RecurringDirectDebitPayment, Order, OrderStatuses, Donation
from bluebottle.projects.models import Project
from ...mails import mail_monthly_donation_processed_notification

logger = logging.getLogger(__name__)


#
# Run with:
# ./manage.py process_monthly_donations -v 2 --settings=bluebottle.settings.local (or .production etc.)
#

class Command(BaseCommand):
    help = 'Process monthly donations.'
    requires_model_validation = True

    verbosity_loglevel = {
        '0': logging.ERROR,    # 0 means no output.
        '1': logging.WARNING,  # 1 means normal output (default).
        '2': logging.INFO,     # 2 means verbose output.
        '3': logging.DEBUG     # 3 means very verbose output.
    }

    option_list = BaseCommand.option_list + (
        make_option('--prepare', action='store_true', dest='prepare', default=False,
                    help="Prepare the monthly donations and create records that can be processed later."),

        make_option('--process', action='store_true', dest='process', default=False,
                    help="Process the prepared records."),

        make_option('--csv-export', action='store_true', dest='csv_export', default=False,
                    help="Generate CSV export of monthly donors with donations amounts."),

    )

    def handle(self, *args, **options):
        # Setup the log level for root logger.
        loglevel = self.verbosity_loglevel.get(options['verbosity'])
        logger.setLevel(loglevel)

        recurring_payments_queryset = RecurringDirectDebitPayment.objects.filter(active=True, manually_process=False)
        if options['prepare']:
                prepare_monthly_donations(recurring_payments_queryset, False)


def generate_monthly_donations_csv(recurring_payments_queryset):
    csv_path = os.path.expanduser('~/monthly-donors-{0}.csv'.format(timezone.now().date()))
    logger.info("Saving monthly donations CSV file to:")
    logger.info("  {0}".format(csv_path))
    with open(csv_path, 'wb') as csv_file:
        csvwriter = csv.writer(csv_file, dialect='excel')
        csvwriter.writerow(['Member', 'Active', 'Amount'])
        for rp in recurring_payments_queryset:
            csvwriter.writerow([rp.user.email, rp.active, rp.amount])


def update_last_donation(donation, remaining_amount, popular_projects):
    """
    Updates the last donation with the remaining amount of the payment. If the donation is more than the project
    needs, the project will be filled and the balance will be used to fill the popular projects recursively.
    """
    project = Project.objects.get(id=donation.project_id)

    # Base case.
    if project.amount_donated + (remaining_amount/100) <= project.amount_asked or len(popular_projects) == 0:
        # The remaining amount won't fill up the project or we have no more projects to try. We're done.
        logger.debug(u"Donation is less than project '{0}' needs. No further adjustments are needed.".format(project.title))
        donation.amount = remaining_amount
        donation.save()
        return

    # Recursive case.
    else:
        # Fill up the project.
        logger.debug(u"Donation is more than project '{0}' needs. Filling up project and creating new donation.".format(project.title))
        donation.amount = (project.amount_asked - project.amount_donated) * 100
        donation.save()

        # Create a new Donation and recursively update it with the remaining amount.
        new_project = popular_projects.pop(0)
        new_donation = MonthlyDonation.objects.create(user=donation.user, project=new_project, amount=0)
        update_last_donation(new_donation, remaining_amount - donation.amount, popular_projects)


def create_recurring_order(user, projects, batch, order=None):
    """
    Creates a recurring Order with donations to the supplied projects.
    """
    if not order:
        order = MonthlyOrder.objects.create(user=user, batch=batch)

    for p in projects:
        project = Project.objects.get(id=p.id)
        if project.status == ProjectPhase.objects.get(slug="campaign"):
            MonthlyDonation.objects.create(user=user, project=project, amount=0, order=order)
    return order


def remove_order(order):
    for donation in order.donations.all():
        donation.delete()
    order.delete()


def correct_donation_amounts(popular_projects, recurring_order, recurring_payment):
    """
    Divides the total amount for the monthly donation across all projects. This method deals with the case of a
    donation filling up a project.
    """
    remaining_amount = recurring_payment.amount
    num_donations = recurring_order.donations.count()
    amount_per_project = Decimal(int(math.floor(recurring_payment.amount / num_donations)))
    donations = recurring_order.donations.all()
    logger.info("Processing {0} donations".format(len(donations)))
    for i in range(0, num_donations - 1):
        donation = donations[i]
        project = Project.objects.get(id=donation.project_id)
        if project.amount_donated + (amount_per_project/100) > project.amount_asked:
            donation.amount = 100 * (project.amount_asked - project.amount_donated)
        else:
            donation.amount = amount_per_project
        donation.save()
        remaining_amount -= donation.amount
    update_last_donation(donations[num_donations - 1], remaining_amount, popular_projects)


def prepare_monthly_donations(recurring_payments_queryset, send_email):
    """ The starting point for creating DocData payments for the monthly donations. """

    batch = MonthlyBatch.objects.create(date=now())
    batch.save()

    recurring_donation_errors = []
    RecurringDonationError = namedtuple('RecurringDonationError', 'recurring_payment error_message')
    skipped_recurring_payments = []
    SkippedRecurringPayment = namedtuple('SkippedRecurringPayment', 'recurring_payment orders')
    donation_count = 0

    # The adapter is used after the recurring Order and donations have been adjusted. It's created here so that we can
    # reuse it to process all recurring donations.
    webdirect_payment_adapter = WebDirectDocDataDirectDebitPaymentAdapter()

    # Fixed lists of the popular projects.
    popular_projects_all = list(Project.objects.exclude(skip_monthly=True).filter(status=ProjectPhase.objects.get(slug="campaign")).order_by('-popularity'))
    top_three_projects = popular_projects_all[:3]
    popular_projects_rest = popular_projects_all[3:]

    logger.info("Config: Using these projects as 'Top Three':")
    for project in top_three_projects:
        logger.info("  {0}".format(project.title.encode("utf8")))

    # The main loop that processes each monthly donation.
    for recurring_payment in recurring_payments_queryset:
        top_three_donation = False
        user_selected_projects = []

        # Skip payment if there has been a recurring Order recently.
        ten_days_ago = timezone.now() + timezone.timedelta(days=-10)
        recent_closed_recurring_orders = MonthlyOrder.objects.filter(batch=batch, user=recurring_payment.user, updated__gt=ten_days_ago, amount=recurring_payment.amount)
        if recent_closed_recurring_orders.count() > 0:
            skipped_recurring_payments.append(SkippedRecurringPayment(recurring_payment, list(recent_closed_recurring_orders)))
            logger.warn(
                "Skipping '{0}' because it looks like it has been processed recently with one of these Orders:".format(
                    recurring_payment))
            for closed_order in recent_closed_recurring_orders:
                logger.warn("  Order Number: {0}".format(closed_order.order_number))
            continue

        # Check if there is a monthly shopping cart (Order status is 'recurring') for this recurring_payment user.
        try:
            order = Order.objects.get(user=recurring_payment.user, status=OrderStatuses.recurring)
            recurring_order = MonthlyOrder.objects.create(batch=batch, user=order.user, amount=order.total)
            recurring_order.save()
            for don in order.donations.all():
                donation = MonthlyDonation.objects.create(user=order.user, project=don.project, order=recurring_order, amount=don.amount)
                donation.save()
            logger.debug("Using existing recurring Order for user: {0}.".format(recurring_payment.user))
        except Order.DoesNotExist:
            # There is no monthly shopping cart. The user is supporting the top three projects so we need to create an
            # Order with Donations for the top three projects.
            logger.debug("Creating new 'Top Three' recurring Order for user {0}.".format(recurring_payment.user))
            recurring_order = create_recurring_order(recurring_payment.user, top_three_projects, batch)
            top_three_donation = True
        except MonthlyOrder.MultipleObjectsReturned:
            error_message = "Multiple Orders with status 'recurring' returned for '{0}'. Not processing this recurring donation.".format(
                recurring_payment)
            logger.error(error_message)
            recurring_donation_errors.append(RecurringDonationError(recurring_payment, error_message))
            continue

        # Check if we're above the DocData minimum for direct debit.
        if recurring_payment.amount < 113:
            # Cleanup the Order if there's an error.
            if top_three_donation:
                remove_order(recurring_order)
            error_message = "Payment amount for '{0}' is less than the DocData minimum for direct debit (113). Skipping.".format(
                recurring_payment)
            logger.error(error_message)
            recurring_donation_errors.append(RecurringDonationError(recurring_payment, error_message))
            continue

        # Remove donations to projects that are no longer in the campaign phase.
        for donation in recurring_order.donations.all():
            project = Project.objects.get(id=donation.project.id)
            if project.amount_needed <= 0:
                donation.delete()

        if recurring_order.donations.count() > 0:
            # There are donations in the recurring Order and we need to redistribute / correct the donation amounts.

            # Save a copy of the projects that have been selected by the user so that the monthly shopping cart can
            # recreated after the payment has been successfully started.
            for donation in recurring_order.donations.all():
                user_selected_projects.append(donation.project)

            correct_donation_amounts(popular_projects_all, recurring_order, recurring_payment)
        else:
            # There are no donations in the recurring Order so we need to create a monthly shopping cart to support the
            # top three projects and redistribute / correct the donation amounts.
            create_recurring_order(recurring_payment.user, top_three_projects, batch, recurring_order)

            if recurring_order.donations.count() == 0:
                logger.debug("The top three donations are full. Using next three projects for top three.")
                top_three_projects = popular_projects_rest[:3]
                popular_projects_rest = popular_projects_rest[3:]
                create_recurring_order(recurring_payment.user, top_three_projects, batch, recurring_order)

            correct_donation_amounts(popular_projects_rest, recurring_order, recurring_payment)
            top_three_donation = True

        # At this point the order should be correctly setup and ready for the DocData payment.
        if top_three_donation:
            donation_type_message = "supporting the 'Top Three' projects"
        else:
            donation_type_message = "with {0} donations".format(recurring_order.donations.count())
        logger.info("Starting payment for '{0}' {1}.".format(recurring_payment, donation_type_message))

        # Safety check to ensure the modifications to the donations in the recurring result in an Order total that
        # matches the RecurringDirectDebitPayment.
        if recurring_payment.amount != recurring_order.amount:
            # Cleanup the Order if there's an error.
            recurring_order.amount = recurring_payment.amount
            recurring_order.save()
            # error_message = "RecurringDirectDebitPayment amount: {0} does not equal recurring Order amount: {1} for '{2}'. Not processing this recurring donation.".format(
            #     recurring_payment.amount, recurring_order.amount, recurring_payment)
            # if top_three_donation:
            #     remove_order(recurring_order)
            # logger.error(error_message)
            # recurring_donation_errors.append(RecurringDonationError(recurring_payment, error_message))
            # continue

        # Check if the IBAN / BIC is stored correctly on the RecurringDirectDebitPayment.
        if recurring_payment.iban == '' or recurring_payment.bic == '' or \
                not recurring_payment.iban.endswith(recurring_payment.account) or \
                recurring_payment.bic[:4] != recurring_payment.iban[4:8]:

            # Cleanup the Order if there's an error.
            if top_three_donation:
                remove_order(recurring_order)

            error_message = "Cannot create payment because the IBAN and/or BIC are not available."
            logger.error(error_message)
            recurring_donation_errors.append(RecurringDonationError(recurring_payment, error_message))
            continue

        # Create and fill in the DocDataPaymentOrder.
        # payment = DocDataPaymentOrder()
        # payment.order = recurring_order
        # payment.payment_method_id = 'dd-webdirect'
        #
        # payment.amount = recurring_payment.amount
        # payment.currency = recurring_payment.currency
        #
        # payment.customer_id = recurring_payment.user.id
        # payment.email = recurring_payment.user.email
        #
        # # Use the recurring payment name (bank account name) to set the first and last name if they're not set.
        # if not recurring_payment.user.first_name:
        #     if ' ' in recurring_payment.name:
        #         payment.first_name = recurring_payment.name.split(' ')[0]
        #     else:
        #         payment.first_name = recurring_payment.name
        # else:
        #     payment.first_name = recurring_payment.user.first_name
        #
        # if not recurring_payment.user.last_name:
        #     if ' ' in recurring_payment.name:
        #         payment.last_name = recurring_payment.name[recurring_payment.name.index(' ') + 1:]
        #     else:
        #         payment.last_name = recurring_payment.name
        # else:
        #     payment.last_name = recurring_payment.user.last_name
        #
        # # Try to use the address from the profile if it's set.
        # address = recurring_payment.user.address
        # if not address:
        #     # Cleanup the Order if there's an error.
        #     if top_three_donation:
        #         remove_order(recurring_order)
        #     error_message = "Cannot create a payment for '{0}' because user does not have an address set.".format(recurring_payment)
        #     logger.error(error_message)
        #     recurring_donation_errors.append(RecurringDonationError(recurring_payment, error_message))
        #     continue
        #
        # # Set a default value for the pieces of the address that we don't have.
        # unknown_value = u'Unknown'
        # if not address.line1:
        #     logger.warn("User '{0}' does not have their street and street number set. Using '{1}'.".format(recurring_payment.user, unknown_value))
        #     payment.address = unknown_value
        # else:
        #     payment.address = address.line1
        # if not address.city:
        #     logger.warn("User '{0}' does not have their city set. Using '{1}'.".format(recurring_payment.user, unknown_value))
        #     payment.city = unknown_value
        # else:
        #     payment.city = address.city
        # if not address.postal_code:
        #     logger.warn("User '{0}' does not have their postal code set. Using '{1}'.".format(recurring_payment.user, unknown_value))
        #     payment.postal_code = unknown_value
        # else:
        #     payment.postal_code = address.postal_code
        #
        # # Assume the Netherlands when country not set.
        # if address.country:
        #     payment.country = address.country.alpha2_code
        # else:
        #     payment.country = 'NL'
        #
        # # Try to use the language from the User settings if it's set.
        # if recurring_payment.user.primary_language:
        #     payment.language = recurring_payment.user.primary_language[:2]  # Cut off locale.
        # else:
        #     payment.language = 'nl'
        #
        # payment.save()
        #
        # # Start the WebDirect payment.
        # try:
        #     webdirect_payment_adapter.create_remote_payment_order(payment)
        # except DocDataPaymentException as e:
        #     # Cleanup the Order if there's an error.
        #     if top_three_donation:
        #         remove_order(recurring_order)
        #
        #     error_message = "Problem creating remote payment order."
        #     logger.error(error_message)
        #     recurring_donation_errors.append(
        #         RecurringDonationError(recurring_payment, "{0} {1}".format(error_message, e.message)))
        #     continue
        # else:
        #     recurring_order.status = OrderStatuses.closed
        #     recurring_order.save()
        #
        # try:
        #     webdirect_payment_adapter.start_payment(payment, recurring_payment)
        # except DocDataPaymentException as e:
        #
        #     # Cleanup the Order if there's an error.
        #     if top_three_donation:
        #         remove_order(recurring_order)
        #     else:
        #         recurring_order.status = OrderStatuses.recurring
        #         recurring_order.save()
        #
        #     error_message = "Problem starting payment."
        #     logger.error(error_message)
        #     recurring_donation_errors.append(
        #         RecurringDonationError(recurring_payment, "{0} {1}".format(error_message, e.message)))
        #     continue
        #
        # logger.debug("Payment for '{0}' started.".format(recurring_payment))
        # donation_count += 1
        #
        # # Send an email to the user.
        # if send_email:
        #     mail_monthly_donation_processed_notification(recurring_payment, recurring_order)
        #
        # # Create a new recurring Order (monthly shopping cart) for donations that are not to the 'Top Three'.
        # if not top_three_donation and len(user_selected_projects) > 0:
        #     new_recurring_order = create_recurring_order(recurring_payment.user, user_selected_projects)
        #
        #     # Adjust donation amounts in a simple way for the recurring Order (the monthly donations shopping cart).
        #     num_donations = new_recurring_order.donations.count()
        #     amount_per_project = math.floor(recurring_payment.amount / num_donations)
        #     donations = new_recurring_order.donations.all()
        #     for i in range(0, num_donations - 1):
        #         donation = donations[i]
        #         donation.amount = amount_per_project
        #         donation.save()
        #     # Update the last donation with the remaining amount.
        #     donation = donations[num_donations - 1]
        #     donation.amount = recurring_payment.amount - (amount_per_project * (num_donations - 1))
        #     donation.save()

    logger.info("")
    logger.info("Recurring Donation Processing Summary")
    logger.info("=====================================")
    logger.info("")
    logger.info("Total number of recurring donations: {0}".format(recurring_payments_queryset.count()))
    logger.info("Number of recurring Orders successfully processed: {0}".format(donation_count))
    logger.info("Number of errors: {0}".format(len(recurring_donation_errors)))
    logger.info("Number of skipped payments: {0}".format(len(skipped_recurring_payments)))

    if len(recurring_donation_errors) > 0:
        logger.info("")
        logger.info("")
        logger.info("Detailed Error List")
        logger.info("===================")
        logger.info("")
        for error in recurring_donation_errors:
            logger.info("RecurringDirectDebitPayment: {0} {1}".format(error.recurring_payment.id, error.recurring_payment))
            logger.info("Error: {0}".format(error.error_message))
            logger.info("--")

    if len(skipped_recurring_payments) > 0:
        logger.info("")
        logger.info("")
        logger.info("Skipped Recurring Payments")
        logger.info("==========================")
        logger.info("")
        for skipped_payment in skipped_recurring_payments:
            logger.info("RecurringDirectDebitPayment: {0} {1}".format(skipped_payment.recurring_payment.id, skipped_payment.recurring_payment))
            for closed_order in skipped_payment.orders:
                logger.info("Order Number: {0}".format(closed_order.order_number))
                logger.info("--")
