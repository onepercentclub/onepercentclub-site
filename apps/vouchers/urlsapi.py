from django.conf.urls import patterns


urlpatterns = patterns('',
    # Voucher code is disabled for now.
    #
    # surl(r'^orders/<order_pk:#>/vouchers/$', OrderVoucherList.as_view(), name='fund-order-voucher-list'),
    # surl(r'^orders/<order_pk:#>/vouchers/<pk:#>$', OrderVoucherDetail.as_view(), name='fund-order-voucher-detail'),
    #
    # url(r'^orders/current/vouchers/$', OrderVoucherList.as_view(), {'alias': 'current'}, name='fund-order-current-voucher-list'),
    # surl(r'^orders/current/vouchers/<pk:#>$', OrderVoucherDetail.as_view(), {'alias': 'current'}, name='fund-order-current-voucher-detail'),
    #
    # # Vouchers
    # surl(r'^vouchers/<code:s>$', VoucherDetail.as_view(), name='voucher-detail'),
    # surl(r'^vouchers/<code:s>/donations/$', VoucherDonationList.as_view(), name='voucher-donation-list'),
    # surl(r'^vouchers/<code:s>/donations/<pk:#>$', VoucherDonationDetail.as_view(), name='voucher-donation-list'),
    # surl(r'^customvouchers/$', CustomVoucherRequestList.as_view(), name='custom-voucher-request-list'),
)
