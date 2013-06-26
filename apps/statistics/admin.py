from django.contrib import admin
from .models import Statistic


class StatisticAdmin(admin.ModelAdmin):
    model = Statistic

admin.site.register(Statistic, StatisticAdmin)
