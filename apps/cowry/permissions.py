from rest_framework import permissions


class IsOrderCreator(permissions.BasePermission):
    """
    Allows the access to a payment or order only if the user created the Order that the payment belongs to.
    """
    def has_object_permission(self, request, view, obj):
        # Use duck typing to check if we have an order or a payment.
        if hasattr(obj, 'user'):
            order = obj
        else:
            order = obj.order

        # Case 1: Authenticated user.
        if request.user.is_authenticated():
            # Permission is only granted if the order user is the logged in user.
            return order.user == request.user

        # Case 2: Anonymous user.
        else:
            # For an anonymous user we grant access if the cart order id is the same as the payment order id.
            order_id = request.session.get('cart_order_id')
            if order_id:
                return order_id == order.id
            return False
