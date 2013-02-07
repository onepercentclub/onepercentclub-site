from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import (FundApi, OrderList, OrderDetail, OrderCurrent, OrderProfileCurrent,
                    OrderItemList, OrderDonationList, OrderDonationDetail, OrderLatestItemList, OrderLatestDonationList,
                    PaymentMethodList, PaymentMethodDetail,
                    PaymentList, PaymentDetail, PaymentCurrent,
                    PaymentInfoList, PaymentInfoDetail, PaymentInfoCurrent)

urlpatterns = patterns('',
    url(r'^$', FundApi.as_view(), name='fund-order-list'),

    url(r'^orders/$', OrderList.as_view(), name='fund-order-list'),
    surl(r'^orders/<pk:#>$', OrderDetail.as_view(), name='fund-order-detail'),
    url(r'^orders/current$', OrderCurrent.as_view(), name='fund-order-current'),
    url(r'^orders/latest/items/$', OrderLatestItemList.as_view(), name='fund-order-latest-item-list'),
    url(r'^orders/current/items/$', OrderItemList.as_view(), name='fund-order-current-item-list'),
    url(r'^orders/current/donations/$', OrderDonationList.as_view(), name='fund-order-current-donation-list'),
    url(r'^orders/latest/donations/$', OrderLatestDonationList.as_view(), name='fund-order-latest-donation-list'),
    surl(r'^orders/current/donations/<pk:#>$', OrderDonationDetail.as_view(), name='fund-order-current-donation-detail'),

    surl(r'^orders/profiles/current$', OrderProfileCurrent.as_view(), name='fund-order-profile-current'),


    url(r'^paymentmethods/$', PaymentMethodList.as_view(), name='fund-paymentmethod-list'),
    surl(r'^paymentmethods/<pk:#>$', PaymentMethodDetail.as_view(), name='fund-paymentmethod-detail'),

    url(r'^payments/$', PaymentList.as_view(), name='fund-payment-list'),
    surl(r'^payments/<pk:#>$', PaymentDetail.as_view(), name='fund-payment-detail'),
    url(r'^payments/current$', PaymentCurrent.as_view(), name='fund-payment-current'),

    url(r'^paymentinfo/$', PaymentInfoList.as_view(), name='fund-paymentinfo-list'),
    surl(r'^paymentinfo/<pk:#>$', PaymentInfoDetail.as_view(), name='fund-paymentinfo-detail'),
    url(r'^paymentinfo/current$', PaymentInfoCurrent.as_view(), name='fund-paymentinfo-current'),

)
