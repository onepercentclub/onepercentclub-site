import ipdb

import os
import sys
import datetime
import csv

from django.conf import settings

from fund.models import Donation

"""
These scripts will be superseded by functionality implemented in the
admin framework. However, it seemed important to retain historical
queries for reference purposes.
"""

def run():
    year = 2013
    filename = os.path.join(
        settings.PROJECT_ROOT, 'exports/donations_%d.csv' % year
    )

    fields = (
        'id', 'donation_type', 'created', 'name', 'username',
        'project_id', 'project', 'amount', 'fee_total',
        'amount_psp_fee', 'amount_service_fee', 'amount_organisation_fee',
        'amount_bank_costs_direct', 'amount_bank_costs_indirect',
        'status', 'payment_method', 'bank_date'
    )

    with open(filename, 'wb') as donations_file:
        writer = csv.DictWriter(
            donations_file, fieldnames=fields
        )

        # Write fieldnames header
        fieldnames_dict = {}
        for field in fields:
            fieldnames_dict[field] = field

        writer.writerow(fieldnames_dict)

        # Raw query
        donations = Donation.objects.all()

        # Add related users and projects
        donations = donations.select_related('user', 'project')

        start_date = datetime.date(year=year, month=1, day=1)
        end_date = datetime.date(year=year+1, month=1, day=1)

        # Filter by date
        donations = donations.filter(
            created__gte=start_date, created__lt=end_date
        )

        print 'Exporting %d donations to %s' % (donations.count(), filename)

        counter = 0
        for donation in donations:
            donation_dict = {
                'id': donation.id,
                'donation_type': donation.donation_type,
                'created': donation.created.date().isoformat(),
                'name': donation.user_id and donation.user.get_full_name() or 'Onbekend',
                'username': donation.user_id and donation.user.username or 'Onbekend',
                'project_id': donation.project_id,
                'project': unicode(donation.project),
                'amount': donation.amount/100,
                # fee_total, amount_psp_fee, amount_service_fee,
                # amount_organisation_fee, amount_bank_costs_direct
                # amount_bank_costs_indirect
                'status': donation.status,
                'payment_method': donation.payment_method
                #donations.bank_date
            }

            # Get payment object
            order = donation.order
            if order:
                latest_payment = order.latest_payment

                if order.status == 'paid' and latest_payment.amount != order.total:
                    print 'Payment amount inconsistent with order total: %f versus %f' % (
                        latest_payment.amount/100, donation.amount/100
                    )

                # donation_dict['fee_total'] = latest_payment.fee

            # Convert string values to UTF-8
            for (key, value) in donation_dict.iteritems():
                if isinstance(value, basestring):
                    donation_dict[key] = value.encode('utf-8')

            writer.writerow(donation_dict)

            counter += 1

            if counter % 10 == 0:
                # Report to the terminal every 10 objects
                sys.stdout.write('.')
                sys.stdout.flush()
