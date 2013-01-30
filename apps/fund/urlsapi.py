from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import (FundApi, OrderList, OrderDetail, OrderCurrent,
                    OrderItemList, OrderDonationList, OrderDonationDetail, OrderItemListFinal,
                    PaymentMethodList, PaymentMethodDetail,
                    PaymentList, PaymentDetail, PaymentCurrent,
                    PaymentInfoList, PaymentInfoDetail, PaymentInfoCurrent)

urlpatterns = patterns('',
    # These two urls are not functioning yet
    # TODO: Make it so
    url(r'^$', FundApi.as_view(), name='fund-order-list'),

    url(r'^orders/$', OrderList.as_view(), name='fund-order-list'),
    surl(r'^orders/<pk:#>$', OrderDetail.as_view(), name='fund-order-detail'),
    url(r'^orders/current$', OrderCurrent.as_view(), name='fund-order-current'),
    url(r'^orders/current/itemsfinal/$', OrderItemListFinal.as_view(), name='fund-order-listcurrent-final'),
    url(r'^orders/current/items/$', OrderItemList.as_view(), name='fund-order-current-item-list'),
    url(r'^orders/current/donations/$', OrderDonationList.as_view(), name='fund-order-current-donation-list'),
    surl(r'^orders/current/donations/<pk:#>$', OrderDonationDetail.as_view(), name='fund-order-current-donation-detail'),

    url(r'^paymentmethods/$', PaymentMethodList.as_view(), name='fund-paymentmethod-list'),
    surl(r'^paymentmethods/<pk:#>$', PaymentMethodDetail.as_view(), name='fund-paymentmethod-detail'),

    url(r'^payments/$', PaymentList.as_view(), name='fund-payment-list'),
    surl(r'^payments/<pk:#>$', PaymentDetail.as_view(), name='fund-payment-detail'),
    url(r'^payments/current$', PaymentCurrent.as_view(), name='fund-payment-current'),

    url(r'^paymentinfo/$', PaymentInfoList.as_view(), name='fund-paymentinfo-list'),
    surl(r'^paymentinfo/<pk:#>$', PaymentInfoDetail.as_view(), name='fund-paymentinfo-detail'),
    url(r'^paymentinfo/current$', PaymentInfoCurrent.as_view(), name='fund-paymentinfo-current'),

)
