import ipdb

import os
import sys
import datetime
import csv

from django.conf import settings

from apps.fund.models import Order

"""
These scripts will be superseded by functionality implemented in the
admin framework. However, it seemed important to retain historical
queries for reference purposes.
"""

def run():
    year = 2013
    filename = os.path.join(
        settings.PROJECT_ROOT, 'exports/orders_%d.csv' % year
    )

    fields = (
        # Native order fields
        'id', 'status', 'recurring', 'order_number', 'created',

        # Common cowry payment fields
        'payments__currency', 'payments__amount', 'payments__fee',

        # Docdata related fields
        'payments__docdatapaymentorder__first_name',
        'payments__docdatapaymentorder__last_name',
        'payments__docdatapaymentorder__address',
        'payments__docdatapaymentorder__postal_code',
        'payments__docdatapaymentorder__city',
        'payments__docdatapaymentorder__country',
        'payments__docdatapaymentorder__email',
        'payments__docdatapaymentorder__docdata_payments__docdatawebdirectdirectdebit__account_name',
        'payments__docdatapaymentorder__docdata_payments__docdatawebdirectdirectdebit__account_city',
        'payments__docdatapaymentorder__docdata_payments__docdatawebdirectdirectdebit__bic',
        'payments__docdatapaymentorder__docdata_payments__docdatawebdirectdirectdebit__iban',

        'payments__docdatapaymentorder__docdata_payments__payment_method',
        'payments__docdatapaymentorder__docdata_payments__payment_id'
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
        qs = Order.objects.all()

        # Add related users and projects
        # qs = qs.select_related('user', 'project')

        # Only consider paid orders (for now)
        qs = qs.filter(payments__status='paid')

        start_date = datetime.date(year=year, month=1, day=1)
        end_date = datetime.date(year=year+1, month=1, day=1)

        # Filter by date
        qs = qs.filter(
            created__gte=start_date, created__lt=end_date
        )

        # Make sure it's sorted by creation date
        qs = qs.order_by('created')

        # Select relevant values
        qs = qs.values(*fields)

        print 'Exporting %d orders to %s' % (qs.count(), filename)

        counter = 0
        for obj in qs:
            # Convert string values to UTF-8
            for (key, value) in obj.iteritems():
                if isinstance(value, basestring):
                    obj[key] = value.encode('utf-8')

            writer.writerow(obj)

            counter += 1

            if counter % 10 == 0:
                # Report to the terminal every 10 objects
                sys.stdout.write('.')
                sys.stdout.flush()
