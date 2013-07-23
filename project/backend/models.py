from django.db import models
from django.contrib.auth.models import User
from django.conf import settings as s
from django.utils.translation import ugettext_lazy as _


class userProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    maxDoms = models.IntegerField(default=s.MAX_FREE)
    global_records_per_zone = models.IntegerField(default=1000)
    phone = models.CharField(max_length=192, blank=True)
    alternate_email = models.EmailField(blank=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    prefered_language = models.CharField(max_length=10, choices=s.LANGUAGES, blank=True, null=True)
    public_profile_field = models.BooleanField(default=False)
    has_api = models.BooleanField(default=True)

    class Meta:
        db_table = u'auth_userprofile'


class DnsRecords(models.Model):
    zone = models.CharField(max_length=192, blank=True, db_index=True)
    host = models.CharField(max_length=192, blank=True, db_index=True)
    type = models.CharField(max_length=24, blank=True, default='3600', db_index=True)
    data = models.TextField(blank=True)
    ttl = models.IntegerField(default=3600)
    priority = models.IntegerField(null=True, blank=True)
    refresh = models.IntegerField(default=3600)
    retry = models.IntegerField(default=3600)
    expire = models.IntegerField(default=86400)
    minimum = models.IntegerField(default=3600)
    serial = models.IntegerField(default=2008082700)
    resp_person = models.CharField(max_length=192, default='resp.person.email')
    primary_ns = models.CharField(max_length=192, default='ns1.yourdns.here')
    data_count = models.IntegerField(default=0)

    class Meta:
        db_table = u'dns_records'


class suffixes(models.Model):
    name = models.CharField(max_length=64, blank=False, null=False)


class dnsZones(models.Model):
    zone_name = models.CharField(max_length=192, blank=False, null=False, unique=True)
    add_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_update = models.DateTimeField(auto_now_add=True, auto_now=True)
    owner = models.ForeignKey(User)

    class Meta:
        db_table = u'Zones'

    def __unicode__(self):
        return u'%s' % (self.zone_name)


class zoneMeta(models.Model):
    zone_name = models.ForeignKey(dnsZones)
    max_records = models.IntegerField(default=1000)

    class Meta:
        db_table = u'dns_zonemeta'


class ServiceTemplates(models.Model):
    owner = models.ForeignKey(User, null=True, blank=False)
    name = models.CharField(max_length=192, blank=False, null=False)
    data = models.TextField(null=False, blank=False)

    class Meta:
        db_table = u'services_servicetemplates'


class ZoneServices(models.Model):
    zone_name = models.ForeignKey(dnsZones, null=False, blank=False)
    template = models.ForeignKey(ServiceTemplates, null=False, blank=False)
    record_ids = models.TextField(null=False, blank=False)

    class Meta:
        unique_together = (("zone_name", "template"),)
        db_table = u'services_zoneservices'


class ZoneShares(models.Model):
    zone = models.ForeignKey(dnsZones)
    user = models.ForeignKey(User)

    class Meta:
        unique_together = (("zone", "user"),)
