from django.dispatch import Signal

payment_status_changed = Signal(providing_args=["old_status", "new_status"])
