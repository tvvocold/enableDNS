from django.contrib import admin
from project.backend.models import dnsZones, zoneMeta, userProfile, ZoneShares


class userProfileOption(admin.ModelAdmin):
    fk_name = 'user'
    search_fields = ('user__username',)
    list_display = ('user', 'maxDoms', 'phone', 'alternate_email', 'global_records_per_zone', 'has_api')
    raw_id_fields = ('user',)
    list_select_related = True


class dnsZonesOption(admin.ModelAdmin):
    fk_name = 'owner'
    search_fields = ('owner__username',)
    list_display = ('zone_name', 'add_date', 'last_update', 'owner')
    raw_id_fields = ('owner',)
    list_select_related = True


class zoneMetaOption(admin.ModelAdmin):
    fk_name = 'zone_name'
    search_fields = ('zone_name__zone_name',)
    list_display = ('zone_name', 'max_records')


class zoneSharesOption(admin.ModelAdmin):
    search_fields = ('zone__zone_name', 'user__name')
    list_display = ('zone', 'user')


admin.site.register(userProfile, userProfileOption)
admin.site.register(dnsZones, dnsZonesOption)
admin.site.register(zoneMeta, zoneMetaOption)
admin.site.register(ZoneShares, zoneSharesOption)
