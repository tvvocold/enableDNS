# import re
# import json
import datetime
import ipaddr
# from django.conf import settings as s
from project.backend.models import *
from django.forms.formsets import BaseFormSet


def defaultZone(domain, ip=None):
    serial = str(datetime.date.today().strftime("%Y%m%d")) + "00"
    arr = [
        {
            'type': 'SOA',
            'host': '@',
            'data': 'ns.enabledns.com.',
            'ttl': '3600',
            'refresh': '14400',
            'retry': '7200',
            'expire': '1209600',
            'minimum': '3600',
            'serial': serial,
            'resp_person': 'office.rohost.com.'
        },
        {'type': 'NS', 'host': '@', 'data': 'ns.enabledns.com.', 'ttl': '3600'},
        {'type': 'NS', 'host': '@', 'data': 'ns.enabledns.com.', 'ttl': '3600'},
        {'type': 'NS', 'host': '@', 'data': 'ns3.enabledns.com.', 'ttl': '3600'},
        {'type': 'NS', 'host': '@', 'data': 'ns4.enabledns.com.', 'ttl': '3600'},
    ]
    if ip:
        ip = str(ip)
        with_ip = [
            {
                'type': 'A',
                'host': '@',
                'data': ip,
                'ttl': '3600'
            },
            {
                'type': 'A',
                'host': 'www',
                'data': ip,
                'ttl': '3600'
            }
        ]
        arr.extend(with_ip)
    return arr


def validIP(address):
    try:
        ipaddr.IPv4Address(str(address))
    except:
        return False
    return True


def validIPv6(address):
    try:
        ipaddr.IPv6Address(str(address))
    except:
        return False
    return True


def maxDoms(username):
    maxd = 0
    try:
        maxd = username.get_profile().maxDoms
    except:
        pass
    return maxd


def getMaxRecords(domain):
    if isinstance(domain, dnsZones) is False:
        raise Exception('expected a dnsZones object: %s' % str(type(domain)))

    user = domain.owner
    maxProfileRecords = user.get_profile().global_records_per_zone
    try:
        maxMetaRecords = zoneMeta.objects.get(zone_name=domain).max_records
    except:
        maxMetaRecords = maxProfileRecords

    return int(maxMetaRecords)


def updateModified(domain):
    try:
        z = dnsZones.objects.get(zone_name=domain)
    except:
        raise Exception('could not find domain in database')

    try:
        z.last_update = datetime.datetime.now()
        z.save()
    except Exception as err:
        raise Exception('Failed to update timestamp ' + str(err))
    return True


def addQuotes(d):
    tmp = d
    tmp = tmp.strip('"')
    return '"%s"' % tmp


class BaseFormSets(BaseFormSet):

    def clean(self):
        if any(self.errors):
            return
        return self.forms
