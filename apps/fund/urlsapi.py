from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import OrderList, OrderItemList, OrderDonationList, OrderDonationDetail, PaymentMethodList, CheckoutDetail

urlpatterns = patterns('',
    # These two urls are not functioning yet
    # TODO: Make it so
    url(r'^$', OrderList.as_view(), name='fund-order-list'),
    url(r'^cart/$', OrderItemList.as_view(), name='fund-cart-item-list'),

    url(r'^cart/donations/$', OrderDonationList.as_view(), name='fund-cart-donation-detail'),
    surl(r'^cart/donations/<pk:#>$', OrderDonationDetail.as_view(), name='fund-cart-donation-detail'),
    url(r'^paymentmethods/$', PaymentMethodList.as_view(), name='payments-method-list'),
    url(r'^checkout', CheckoutDetail.as_view(), name='payments-current-detail')
)
