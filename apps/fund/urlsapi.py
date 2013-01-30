from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import (OrderList, OrderItemList, OrderDonationList, OrderDonationDetail, PaymentMethodList,
                    PaymentMethodDetail, PaymentCurrent, PaymentStatusDetail,
                    PaymentInfoList, PaymentInfoDetail,
                    PaymentList, PaymentDetail, OrderDetail, FundApi)

urlpatterns = patterns('',
    # These two urls are not functioning yet
    # TODO: Make it so
    url(r'^$', FundApi.as_view(), name='fund-order-list'),

    url(r'^orders/$', OrderList.as_view(), name='fund-order-list'),
    surl(r'^orders/<pk:#>$', OrderDetail.as_view(), name='fund-order-detail'),
    url(r'^orders/current$', OrderDetail.as_view(), name='fund-order-current'),
    url(r'^orders/current/items/$', OrderItemList.as_view(), name='fund-order-current-item-list'),
    url(r'^orders/current/donations/$', OrderDonationList.as_view(), name='fund-order-current-donation-list'),
    surl(r'^orders/current/donations/<pk:#>$', OrderDonationDetail.as_view(), name='fund-order-current-donation-detail'),

    url(r'^paymentmethods/$', PaymentMethodList.as_view(), name='fund-paymentmethod-list'),
    surl(r'^paymentmethods/<pk:#>$', PaymentMethodDetail.as_view(), name='fund-paymentmethod-detail'),

    url(r'^payments/$', PaymentList.as_view(), name='fund-payment-list'),
    surl(r'^payments/<pk:#>$', PaymentDetail.as_view(), name='fund-payment-detail'),
    url(r'^payments/current$', PaymentCurrent.as_view(), name='fund-payment-current'),

    url(r'^paymentinfos/$', PaymentInfoList.as_view(), name='fund-paymentinfo-list'),
    surl(r'^paymentinfos/<pk:#>$', PaymentInfoDetail.as_view(), name='fund-paymentinfo-detail'),
    url(r'^paymentinfos/current$', PaymentInfoDetail.as_view(), name='fund-paymentinfo-current'),

)
