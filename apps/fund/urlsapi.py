from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import (FundApi, OrderList, OrderDetail, CurrentOrder,
                    OrderDonationDetail, OrderLatestDonationList, PaymentOrderProfileCurrent, OrderLatestItemList,
                    PaymentMethodList, VoucherDetail, PaymentMethodInfoCurrent,
                    OrderVoucherList, OrderVoucherDetail, VoucherDonationList, VoucherDonationDetail,
                    CustomVoucherRequestList, OrderDonationList)


urlpatterns = patterns('',
    url(r'^$', FundApi.as_view(), name='fund-order-list'),

    url(r'^orders/$', OrderList.as_view(), name='fund-order-list'),
    surl(r'^orders/<pk:#>$', OrderDetail.as_view(), name='fund-order-detail'),

    # Current Order (i.e. the server-side shopping cart).
    url(r'^orders/current$', CurrentOrder.as_view(), name='fund-order-current'),
    url(r'^orders/current/donations/$', OrderDonationList.as_view(), name='fund-current-order-donation-list'),
    surl(r'^orders/current/donations/<pk:#>$', OrderDonationDetail.as_view(), name='fund-current-order-donation-detail'),
    url(r'^orders/current/vouchers/$', OrderVoucherList.as_view(), name='fund-current-order-voucher-list'),
    surl(r'^orders/current/vouchers/<pk:#>$', OrderVoucherDetail.as_view(), name='fund-current-order-voucher-detail'),

    url(r'^orders/latest/donations/$', OrderLatestDonationList.as_view(), name='fund-order-latest-donation-list'),

    surl(r'^vouchers/<code:s>$', VoucherDetail.as_view(), name='voucher-detail'),
    surl(r'^vouchers/<code:s>/donations/$', VoucherDonationList.as_view(), name='voucher-donation-list'),
    surl(r'^vouchers/<code:s>/donations/<pk:#>$', VoucherDonationDetail.as_view(), name='voucher-donation-list'),
    surl(r'^customvouchers/$', CustomVoucherRequestList.as_view(), name='custom-voucher-request-list'),


    url(r'^paymentorderprofiles/current$', PaymentOrderProfileCurrent.as_view(), name='fund-payment-order-profile-current'),

    url(r'^paymentmethods/$', PaymentMethodList.as_view(), name='fund-payment-method-list'),
    surl(r'^paymentmethods/<slug:s>$', PaymentMethodList.as_view(), name='fund-payment-method-detail'),

    url(r'^paymentmethodinfo/current$', PaymentMethodInfoCurrent.as_view(), name='fund-payment-method-ideal-current'),


)
