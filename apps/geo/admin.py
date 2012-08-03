from .models import Region, SubRegion, Country
from django.contrib import admin


class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'numeric_code')

admin.site.register(Region, RegionAdmin)


class SubRegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'numeric_code')
    list_filter = ('region',)

admin.site.register(SubRegion, SubRegionAdmin)


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'alpha2_code', 'alpha3_code', 'numeric_code')
    list_filter = ('oda_recipient', 'subregion__region', 'subregion')
    search_fields = ('name', 'alpha2_code', 'alpha3_code')

admin.site.register(Country, CountryAdmin)
