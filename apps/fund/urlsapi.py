from django.conf.urls import patterns, include, url
from surlex.dj import surl
from .views import OrderList, OrderDetail, OrderCurrentDetail, PaymentProfileCurrent,  VoucherDetail, \
    OrderVoucherList, OrderVoucherDetail, VoucherDonationList, VoucherDonationDetail,  CustomVoucherRequestList, \
    PaymentCurrent, RecurringDirectDebitPaymentList, RecurringDirectDebitPaymentDetail, OrderCurrentDonationDetail, \
    OrderCurrentDonationList, NestedDonationDetail, NestedDonationList, DonationList, DonationDetail, TickerList


urlpatterns = patterns('',
    # Orders
    url(r'^orders/$', OrderList.as_view(), name='fund-order-list'),
    surl(r'^orders/<pk:#>$', OrderDetail.as_view(), name='fund-order-detail'),
    surl(r'^orders/<order_pk:#>/donations/$', NestedDonationList.as_view(), name='fund-order-donation-list'),
    surl(r'^orders/<order_pk:#>/donations/<pk:#>$', NestedDonationDetail.as_view(), name='fund-order-donation-detail'),
    # Voucher code is disabled for now.
    # surl(r'^orders/<order_pk:#>/vouchers/$', OrderVoucherList.as_view(), name='fund-order-voucher-list'),
    # surl(r'^orders/<order_pk:#>/vouchers/<pk:#>$', OrderVoucherDetail.as_view(), name='fund-order-voucher-detail'),

    # Donations
    surl(r'^donations/$', DonationList.as_view(), name='fund-donation-list'),
    surl(r'^donations/<pk:#>$', DonationDetail.as_view(), name='fund-donation-detail'),

    # Latest Donations
    surl(r'^latest-donations/$', TickerList.as_view(), name='fund-ticker-list'),

    # Current Order (i.e. the server-side shopping cart).
    url(r'^orders/current$', OrderCurrentDetail.as_view(), {'alias': 'current'}, name='fund-order-current-detail'),
    url(r'^orders/current/donations/$', OrderCurrentDonationList.as_view(), {'alias': 'current'}, name='fund-order-current-donation-list'),
    surl(r'^orders/current/donations/<pk:#>$', OrderCurrentDonationDetail.as_view(), {'alias': 'current'}, name='fund-order-current-donation-detail'),
    # Voucher code is disabled for now.
    # url(r'^orders/current/vouchers/$', OrderVoucherList.as_view(), {'alias': 'current'}, name='fund-order-current-voucher-list'),
    # surl(r'^orders/current/vouchers/<pk:#>$', OrderVoucherDetail.as_view(), {'alias': 'current'}, name='fund-order-current-voucher-detail'),
    #
    # # Vouchers
    # surl(r'^vouchers/<code:s>$', VoucherDetail.as_view(), name='voucher-detail'),
    # surl(r'^vouchers/<code:s>/donations/$', VoucherDonationList.as_view(), name='voucher-donation-list'),
    # surl(r'^vouchers/<code:s>/donations/<pk:#>$', VoucherDonationDetail.as_view(), name='voucher-donation-list'),
    # surl(r'^customvouchers/$', CustomVoucherRequestList.as_view(), name='custom-voucher-request-list'),

    # Payments
    url(r'^paymentprofiles/current$', PaymentProfileCurrent.as_view(), name='payment-profile-current'),
    url(r'^payments/current$', PaymentCurrent.as_view(), name='payment-current'),
    # The Payment REST API.
    url(r'', include('apps.cowry.urlsapi')),
    url(r'^recurringdirectdebitpayments/$', RecurringDirectDebitPaymentList.as_view(), name='recurring-direct-debit-payment-list'),
    surl(r'^recurringdirectdebitpayments/<pk:#>$', RecurringDirectDebitPaymentDetail.as_view(), name='recurring-direct-debit-payment-detail'),

)
