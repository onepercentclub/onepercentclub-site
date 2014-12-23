import ipdb

import os
import sys
import datetime
import csv

from django.conf import settings

from apps.payouts.models import Payout

"""
These scripts will be superseded by functionality implemented in the
admin framework. However, it seemed important to retain historical
queries for reference purposes.
"""

def run():
    year = 2013
    filename = os.path.join(
        settings.PROJECT_ROOT, 'exports/payouts_%d.csv' % year
    )

    fields = (
        'created', 'project', 'amount_registered', 'amount_psp_fee',
        'amount_service_fee', 'amount_organisation_fee',
        'amount_bank_costs_direct', 'amount_bank_costs_indirect',
        'amount_collected', 'account_number', 'account_name',
        'account_city', 'type', 'status'
    )

    with open(filename, 'wb') as payouts_file:
        writer = csv.DictWriter(
            payouts_file, fieldnames=fields
        )

        # Write fieldnames header
        fieldnames_dict = {}
        for field in fields:
            fieldnames_dict[field] = field

        writer.writerow(fieldnames_dict)

        # Raw query
        qs = Payout.objects.all()

        # Add related users and projects
        # qs = qs.select_related('user', 'project')

        start_date = datetime.date(year=year, month=1, day=1)
        end_date = datetime.date(year=year+1, month=1, day=1)

        # Filter by date
        qs = qs.filter(
            created__gte=start_date, created__lt=end_date
        )

        print 'Exporting %d payouts to %s' % (qs.count(), filename)

        counter = 0
        for obj in qs:
            export_dict = {
                'created': obj.created.date().isoformat(),
                'project': unicode(obj.project),
                'amount_registered': obj.amount_raised,
                # 'amount_psp_fee': ,
                # 'amount_service_fee':,
                # 'amount_organisation_fee':,
                # 'amount_bank_costs_direct':,
                # 'amount_bank_costs_indirect':,
                'amount_collected': obj.amount_payout,
                'account_number': obj.receiver_account_iban or obj.receiver_account_number,
                'account_name': obj.receiver_account_name,
                'account_city': obj.receiver_account_city,
                # 'type':
                'status': obj.status
            }

            # Convert string values to UTF-8
            for (key, value) in export_dict.iteritems():
                if isinstance(value, basestring):
                    export_dict[key] = value.encode('utf-8')

            writer.writerow(export_dict)

            counter += 1

            if counter % 10 == 0:
                # Report to the terminal every 10 objects
                sys.stdout.write('.')
                sys.stdout.flush()
