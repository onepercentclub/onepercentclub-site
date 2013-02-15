from django.contrib import admin
from .models import Donation, Order, OrderItem


class DonationAdmin(admin.ModelAdmin):
    model = Donation
    date_hierarchy = 'created'
    list_display = ('created', 'user', 'amount')
    list_filter = ('status', 'project', 'user')

    search_fields = (
        'user__first_name', 'user__last_name', 'project__title'
    )


admin.site.register(Donation, DonationAdmin)


class OrderItemInline(admin.StackedInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_filter = ('status', 'user')
    list_display = ('created', 'amount', 'status')
    inlines = (OrderItemInline, )


admin.site.register(Order, OrderAdmin)
