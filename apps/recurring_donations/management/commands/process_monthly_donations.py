from decimal import Decimal
import math
import logging
from collections import namedtuple
from optparse import make_option
from bluebottle.payments.exception import PaymentException

from bluebottle.payments.models import OrderPayment
from bluebottle.payments_docdata.exceptions import DocdataPaymentException

from apps.recurring_donations.models import MonthlyProject
from bluebottle.bb_projects.models import ProjectPhase
from bluebottle.utils.model_dispatcher import get_donation_model, get_order_model, get_project_model
from bluebottle.utils.utils import StatusDefinition
from django.utils.timezone import now

from django.core.management.base import BaseCommand
from django.utils import timezone
from bluebottle.payments.services import PaymentService

from ...models import MonthlyDonor, MonthlyDonation, MonthlyOrder, MonthlyBatch
from ...mails import mail_monthly_donation_processed_notification


DONATION_MODEL = get_donation_model()
ORDER_MODEL = get_order_model()
PROJECT_MODEL = get_project_model()

logger = logging.getLogger(__name__)


#
# First step:
# ./manage.py process_monthly_donations --prepare
# ./manage.py process_monthly_donations --process
#
# ./manage.py process_monthly_donations --process-single bart@1procentclub.nl
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
        make_option('--no-email', action='store_true', dest='no_email', default=False,
                help="Don't send the monthly donation email to users (when processing)."),

        make_option('--prepare', action='store_true', dest='prepare', default=False,
                    help="Prepare the monthly donations and create records that can be processed later."),

        make_option('--process', action='store_true', dest='process', default=False,
                    help="Process the prepared records."),

        make_option('--process-single', action='store', dest='process_single',  default=False,
                    metavar='<someone@gmail.com>', type='str',
                    help="Process only the MonthlyOrder for specified e-mail address."),

    )

    def handle(self, *args, **options):
        # Setup the log level for root logger.
        loglevel = self.verbosity_loglevel.get(options['verbosity'])
        logger.setLevel(loglevel)

        send_email = not options['no_email']

        if options['prepare']:
            prepare_monthly_donations()

        if options['process']:
            process_monthly_batch(None, send_email)

        if options['process_single']:
            process_single_monthly_order(options['process_single'], None, send_email)


def create_recurring_order(user, projects, batch, donor):
    """
    Creates a recurring Order with donations to the supplied projects.
    """
    project_amount = Decimal(math.floor(donor.amount * 100 / len(projects))) / 100
    order = MonthlyOrder.objects.create(user=user, batch=batch, amount=donor.amount, name=donor.name,
                                        city=donor.city, iban=donor.iban, bic=donor.bic,
                                        country=donor.country.alpha2_code)
    order.save()

    rest_amount = donor.amount - project_amount * len(projects)

    for p in projects:
        project = PROJECT_MODEL.objects.get(id=p.id)
        don = MonthlyDonation.objects.create(user=user, project=project, amount=project_amount, order=order)
        don.save()

    # Update amount for last donation to make sure donation total == donor amount
    don.amount += rest_amount
    don.save()

    return order


def prepare_monthly_donations():
    """
    Prepare MonthlyOrders.
    """

    ten_days_ago = timezone.now() + timezone.timedelta(days=-10)
    recent_batches = MonthlyBatch.objects.filter(date__gt=ten_days_ago)
    if recent_batches.count() > 0:
        recent_batch = recent_batches.all()[0]
        message = "Found a recent batch {0} : {1}. Refusing to create another one quite now.".format(recent_batch.id, recent_batch)
        logger.error(message)
        return

    batch = MonthlyBatch.objects.create(date=now())
    batch.save()
    top_three_donation = False

    donor_queryset = MonthlyDonor.objects.filter(active=True).order_by('user__email')

    recurring_donation_errors = []
    RecurringDonationError = namedtuple('RecurringDonationError', 'recurring_payment error_message')
    skipped_recurring_payments = []
    SkippedRecurringPayment = namedtuple('SkippedRecurringPayment', 'recurring_payment orders')
    donation_count = 0

    popular_projects_all = PROJECT_MODEL.objects.exclude(skip_monthly=True, amount_needed=0).filter(status=ProjectPhase.objects.get(slug="campaign")).order_by('-popularity')
    top_three_projects = list(popular_projects_all[:3])
    top_projects = list(popular_projects_all[3:])

    logger.info("Config: Using these projects as 'Top Three':")
    for project in top_three_projects:
        logger.info("  {0}".format(project.title.encode("utf8")))

    # The main loop that processes each monthly donation.
    for donor in donor_queryset:

        # Remove DonorProjects for Projects that no longer need money.
        # This is amount_needed from db minus the amount already appointed in previous MonthlyDonations
        for donor_project in donor.projects.all():
            if donor_project.project.status != ProjectPhase.objects.get(slug="campaign"):
                logger.info(u"Project not in Campaign phase. Skipping '{0}'".format(donor_project.project.title))
                donor_project.delete()
            elif donor_project.project.amount_needed <= 0:
                logger.info(u"Project already funded. Skipping '{0}'".format(donor_project.project.title))
                donor_project.delete()
            else:
                monthly_project, created = MonthlyProject.objects.get_or_create(batch=batch, project=donor_project.project)
                if donor_project.project.amount_needed - monthly_project.amount <= 0:
                    logger.info(u"Project already funded. Skipping '{0}'".format(donor_project.project.title))
                    donor_project.delete()

        # Remove Projects from top 3
        for project in top_three_projects:
            monthly_project, created = MonthlyProject.objects.get_or_create(batch=batch, project=project)
            if project.amount_needed - monthly_project.amount <= 0:
                # Remove project if it's doesn't need more many and add another from top_projects
                logger.info(u"Top3 project fully funded. Skipping '{0}'".format(project.title))
                top_three_projects.remove(project)
                new_project = top_projects.pop(0)
                logger.info(u"New Top3 project added '{0}'".format(new_project.title))
                top_three_projects.append(new_project)

        # Check if the donor object is valid
        if not donor.is_valid:
            error_message = "MonthlyDonor [{0}] invalid! IBAN/BIC missing or amount wrong.".format(donor.id)
            logger.error(error_message)
            recurring_donation_errors.append(RecurringDonationError(donor, error_message))
            continue

        # Create MonthlyOrder and MonthlyDonation objects
        if donor.projects.count():
            # Prepare a MonthlyOrder with preferred projects
            preferred_projects = []
            for project in donor.projects.all():
                preferred_projects.append(project.project)
            recurring_order = create_recurring_order(donor.user, preferred_projects, batch, donor)
            logger.debug("Preparing an Order with preferred projects for user: {0}.".format(donor.user))
        else:
            # Prepare MonthlyOrder with Donations for the top three projects.
            logger.debug("Preparing new 'Top Three' Order for user {0}.".format(donor.user))
            recurring_order = create_recurring_order(donor.user, top_three_projects, batch, donor)
            top_three_donation = True

        # Update amounts for projects
        for donation in recurring_order.donations.all():
            monthly_project, created = MonthlyProject.objects.get_or_create(batch=batch, project=donation.project)
            monthly_project.amount += donation.amount
            monthly_project.save()

        # At this point the order should be correctly setup and ready for the DocData payment.
        if top_three_donation:
            donation_type_message = "supporting the 'Top Three' projects"
        else:
            donation_type_message = "with {0} donations".format(recurring_order.donations.count())
        logger.info("Starting payment for '{0}' {1}.".format(donor, donation_type_message))

        # Safety check to ensure the modifications to the donations in the recurring result in an Order total that
        # matches the RecurringDirectDebitPayment.
        if donor.amount != Decimal(recurring_order.amount):
            error_message = "Monthly donation amount: {0} does not equal recurring Order amount: {1} for '{2}'. Not processing this recurring donation.".format(
                donor.amount, recurring_order.amount, donor)
            logger.error(error_message)
            recurring_donation_errors.append(RecurringDonationError(donor, error_message))
            continue

    logger.info("")
    logger.info("Recurring Donation Preparing Summary")
    logger.info("=====================================")
    logger.info("")
    logger.info("Total number of recurring donations: {0}".format(donor_queryset.count()))
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
                logger.info("Order Number: {0}".format(closed_order.id))
                logger.info("--")


def _process_monthly_order(monthly_order, send_email=False):

    if monthly_order.processed:
        logger.info("Order for {0} already processed".format(monthly_order.user))
        return False

    ten_days_ago = timezone.now() + timezone.timedelta(days=-10)
    recent_orders = ORDER_MODEL.objects.filter(user=monthly_order.user, order_type='recurring', updated__gt=ten_days_ago)

    if recent_orders.count() > 0:
        message = "Skipping '{0}' recently processed a recurring order for {1}:".format(monthly_order, monthly_order.user)
        logger.warn(message)
        for closed_order in recent_orders.all():
            logger.warn("Recent Order Number: {0}".format(closed_order.id))

        # Set an error on this monthly order
        monthly_order.error = message
        monthly_order.save()
        return False

    order = ORDER_MODEL.objects.create(status=StatusDefinition.LOCKED, user=monthly_order.user, order_type='recurring')
    order.save()

    logger.info("Creating Order for {0} with {1} donations".format(monthly_order.user, monthly_order.donations.count()))
    for monthly_donation in monthly_order.donations.all():
        donation = DONATION_MODEL.objects.create(amount=monthly_donation.amount, user=monthly_donation.user,
                                                 project=monthly_donation.project, order=order)
        donation.save()

    integration_data = {'account_name': monthly_order.name,
                        'account_city': monthly_order.city,
                        'iban': monthly_order.iban,
                        'bic' :monthly_order.bic,
                        'agree': True}

    order_payment = OrderPayment(order=order, user=monthly_order.user, payment_method='docdataDirectdebit',
                                 integration_data=integration_data)

    order_payment.save()

    try:
        service = PaymentService(order_payment)
        service.start_payment()
    except PaymentException as e:
        order_payment.delete()
        order.delete()
        error_message = "Problem starting payment. {0}".format(e)
        monthly_order.error = "{0}".format(e.message)
        monthly_order.save()
        logger.error(error_message)
        return False

    logger.debug("Payment for '{0}' started.".format(monthly_order))

    monthly_order.processed = True
    monthly_order.error = ''
    monthly_order.save()

    # Try to update status
    service.check_payment_status()

    # Send an email to the user.
    if send_email:
        mail_monthly_donation_processed_notification(monthly_order)

    return True


def process_single_monthly_order(email, batch=None, send_email=False):

    if not batch:
        logger.info("No batch found using latest...")
        batch = MonthlyBatch.objects.order_by('-date', '-created').all()[0]

    monthly_orders = batch.orders.filter(user__email=email)
    if monthly_orders.count() > 1:
        logger.error("Found multiple MonthlyOrders for {0}.".format(email))
    elif monthly_orders.count() == 1:
        monthly_order = monthly_orders.get()
        payment = _process_monthly_order(monthly_order, send_email)
    else:
        logger.error("No MonthlyOrder found for {0} in Batch {1}.".format(email, batch))


def process_monthly_batch(batch=None, send_email=False):
    """
    Process the prepared monthly orders. This will create the actual payments.
    """

    if not batch:
        logger.info("No batch found using latest...")
        batch = MonthlyBatch.objects.order_by('-date', '-created').all()[0]

    for monthly_order in batch.orders.all():
        _process_monthly_order(monthly_order, send_email)
