import csv
import logging
import os
from django.utils import timezone
from django.conf import settings
from apps.fund.models import Donation, DonationStatuses

logger = logging.getLogger(__name__)


def generate_donations_csv_file(loglevel):
    logger.setLevel(loglevel)
    error_count = 0
    success_count = 0

    filename = 'donations-{0}.csv'.format(timezone.now().strftime('%Y-%m-%dT%H:%M:%S'))
    with open(os.path.join(settings.PROJECT_ROOT, filename), 'wb') as csv_outfile:
        csvwriter = csv.writer(csv_outfile, quoting=csv.QUOTE_ALL)

        # TODO get field names from model for csv header.
        # SalesforceDonation._meta.fields

        csvwriter.writerow(["RECEIVER", "AMOUNT", "CLOSEDATE", "ID", "NAME", "ACCOUNTID",
                            "PAYMENT_METHOD__C", "PROJECT__C", "STAGENAME", "TYPE__C", "DONATION_CREATED_DATE__C"])

        donations = Donation.objects.all()
        for donation in donations:
            try:
                receiver_id = ''
                if donation.user:
                    receiver_id = donation.user.id

                project_id = ''
                if donation.project:
                    project_id = donation.project.id

                csvwriter.writerow([receiver_id,                                    # receiver
                                    '%01.2f' % (float(donation.amount) / 100),      # amount
                                    donation.created.date(),                        # closedate
                                    '',                                             # id
                                    '',                                             # name
                                    '',                                             # accountid
                                    '',                                             # payment_method_c
                                    project_id,                                     # project_c
                                    DonationStatuses.values[donation.status],       # stagename
                                    '',                                             # type_c
                                    donation.created.date()])                       # donation_create_date_c
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error("Error while saving donation id {0}: ".format(donation.id) + str(e))

    return success_count, error_count
