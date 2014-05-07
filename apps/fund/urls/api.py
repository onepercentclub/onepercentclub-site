from apps.fund.views import RecurringOrderList, RecurringOrderDetail, RecurringDonationList, RecurringDonationDetail, \
    ProjectDonationList, ProjectSupporterList
from django.conf.urls import patterns, include, url
from surlex.dj import surl
from ..views import OrderList, OrderDetail, OrderCurrentDetail, PaymentProfileCurrent,  PaymentCurrent, \
    RecurringDirectDebitPaymentList, RecurringDirectDebitPaymentDetail, OrderCurrentDonationDetail, \
    OrderCurrentDonationList, NestedDonationDetail, NestedDonationList, DonationList, DonationDetail, TickerList


urlpatterns = patterns('',
    # Orders
    url(r'^orders/$', OrderList.as_view(), name='fund-order-list'),
    surl(r'^orders/<pk:#>$', OrderDetail.as_view(), name='fund-order-detail'),
    surl(r'^orders/<order_pk:#>/donations/$', NestedDonationList.as_view(), name='fund-order-donation-list'),
    surl(r'^orders/<order_pk:#>/donations/<pk:#>$', NestedDonationDetail.as_view(), name='fund-order-donation-detail'),

    # Donations
    surl(r'^project-donations/$', ProjectDonationList.as_view(), name='project-donation-list'),
    surl(r'^project-supporters/$', ProjectSupporterList.as_view(), name='project-supporter-list'),

    # Donations
    surl(r'^donations/$', DonationList.as_view(), name='fund-donation-list'),
    surl(r'^donations/<pk:#>$', DonationDetail.as_view(), name='fund-donation-detail'),

    # Latest Donations
    surl(r'^latest-donations/$', TickerList.as_view(), name='fund-ticker-list'),

    # Current Order (i.e. the server-side shopping cart).
    url(r'^orders/current$', OrderCurrentDetail.as_view(), {'alias': 'current'}, name='fund-order-current-detail'),
    url(r'^orders/current/donations/$', OrderCurrentDonationList.as_view(), {'alias': 'current'}, name='fund-order-current-donation-list'),
    surl(r'^orders/current/donations/<pk:#>$', OrderCurrentDonationDetail.as_view(), {'alias': 'current'}, name='fund-order-current-donation-detail'),

    # Payments
    url(r'^paymentprofiles/current$', PaymentProfileCurrent.as_view(), name='payment-profile-current'),
    url(r'^payments/current$', PaymentCurrent.as_view(), name='payment-current'),


    # Recurring Orders, Donations, Payments
    surl(r'^recurring/orders/$', RecurringOrderList.as_view(), name='fund-recurring-order-list'),
    surl(r'^recurring/orders/<pk:#>$', RecurringOrderDetail.as_view(), name='fund-recurring-order-detail'),

    surl(r'^recurring/donations/$', RecurringDonationList.as_view(), name='fund-recurring-donation-list'),
    surl(r'^recurring/donations/<pk:#>$', RecurringDonationDetail.as_view(), name='fund-recurring-donation-detail'),

    # The Payment REST API.
    url(r'', include('apps.cowry.urls.api')),
    url(r'^recurring/directdebitpayments/$', RecurringDirectDebitPaymentList.as_view(), name='recurring-direct-debit-payment-list'),
    surl(r'^recurring/directdebitpayments/<pk:#>$', RecurringDirectDebitPaymentDetail.as_view(), name='recurring-direct-debit-payment-detail'),


)
