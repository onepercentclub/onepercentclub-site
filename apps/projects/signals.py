from django.dispatch import Signal

# This signal indicates that the supplied project has been funded.
#
# :param first_time_funded: Whether or not the project has reached the funded state before. For instance, a project
#                           can become "unfunded" when a donation that was pending fails.
#
project_funded = Signal(providing_args=["first_time_funded"])
