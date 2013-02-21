from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import (FundApi, OrderList, OrderDetail, OrderCurrent, OrderItemList, OrderDonationList,
                    OrderDonationDetail, OrderLatestDonationList, PaymentOrderProfileCurrent, OrderLatestItemList,
                    PaymentMethodList, VoucherDetail, PaymentMethodInfoCurrent, OrderVoucherList, OrderVoucherDetail)


urlpatterns = patterns('',
    url(r'^$', FundApi.as_view(), name='fund-order-list'),

    url(r'^orders/$', OrderList.as_view(), name='fund-order-list'),
    surl(r'^orders/<pk:#>$', OrderDetail.as_view(), name='fund-order-detail'),
    url(r'^orders/current$', OrderCurrent.as_view(), name='fund-order-current'),
    url(r'^orders/latest/items/$', OrderLatestItemList.as_view(), name='fund-order-latest-item-list'),
    url(r'^orders/current/items/$', OrderItemList.as_view(), name='fund-order-current-item-list'),
    url(r'^orders/current/donations/$', OrderDonationList.as_view(), name='fund-order-current-donation-list'),
    surl(r'^orders/current/donations/<pk:#>$', OrderDonationDetail.as_view(), name='fund-order-current-donation-detail'),

    url(r'^orders/current/vouchers/$', OrderVoucherList.as_view(), name='fund-order-current-voucher-list'),
    surl(r'^orders/current/vouchers/<pk:#>$', OrderVoucherDetail.as_view(), name='fund-order-current-voucher-detail'),
    surl(r'^vouchers/<code:s>$', VoucherDetail.as_view(), name='voucher-detail'),

    url(r'^orders/latest/donations/$', OrderLatestDonationList.as_view(), name='fund-order-latest-donation-list'),


    url(r'^paymentorderprofiles/current$', PaymentOrderProfileCurrent.as_view(), name='fund-payment-order-profile-current'),

    url(r'^paymentmethods/$', PaymentMethodList.as_view(), name='fund-payment-method-list'),
    surl(r'^paymentmethods/<slug:s>$', PaymentMethodList.as_view(), name='fund-payment-method-detail'),

    url(r'^paymentmethodinfo/current$', PaymentMethodInfoCurrent.as_view(), name='fund-payment-method-ideal-current'),


)
