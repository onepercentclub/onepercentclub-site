from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import (OrderList, OrderItemList, OrderDonationList, OrderDonationDetail, PaymentMethodList,
                    PaymentMethodDetail, CheckoutDetail, PaymentStatusDetail, PaymentInfoDetail)

urlpatterns = patterns('',
    # These two urls are not functioning yet
    # TODO: Make it so
    url(r'^$', OrderList.as_view(), name='fund-order-list'),
    url(r'^cart/$', OrderItemList.as_view(), name='fund-cart-item-list'),

    url(r'^cart/donations/$', OrderDonationList.as_view(), name='fund-cart-donation-detail'),
    surl(r'^cart/donations/<pk:#>$', OrderDonationDetail.as_view(), name='fund-cart-donation-detail'),
    url(r'^paymentmethods/$', PaymentMethodList.as_view(), name='fund-paymentmethod-list'),
    surl(r'^paymentmethods/<pk:#>$', PaymentMethodDetail.as_view(), name='fund-paymentmethod-detail'),
    url(r'^checkout', CheckoutDetail.as_view(), name='fund-checkout'),
    url(r'^paymentinfo', PaymentInfoDetail.as_view(), name='fund-paymentinfo'),
    surl(r'^paymentstatus/<status:s>', PaymentStatusDetail.as_view(), name='fund-paymentstatus')
)
