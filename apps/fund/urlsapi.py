from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import OrderList, OrderItemList, OrderDonationList, OrderDonationDetail

urlpatterns = patterns('',
    # These two urls are not functioning yet
    # TODO: Make it so
    url(r'orders/^$', OrderList.as_view(), name='fund-order-list'),
    url(r'^orders/cart/items/$', OrderItemList.as_view(), name='fund-cart-item-list'),

    url(r'^orders/cart/donations/$', OrderDonationList.as_view(), name='fund-cart-donation-detail'),
    surl(r'^orders/cart/donations/<pk:#>$', OrderDonationDetail.as_view(), name='fund-cart-donation-detail'),
)
