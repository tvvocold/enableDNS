from datetime import date
from django.db import transaction
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from project.backend.models import *
from project.backend.Exceptions import *

import re
import project.backend.validators as validators
import project.backend.functions as functions


class Zone(object):

    def __init__(self, user, request=None, format=None, rev_prefix=None):
        if isinstance(user, User) is False:
            raise Exception('Expected User object. Got %s' % str(type(user)))
        self.account = user
        self.request = request
        self.profile = user.get_profile()
        self.format = format or 'json'
        self.rev_prefix = rev_prefix or 'v1_0'

    def build_full_url(self, rev):
        if self.request:
            url = self.request.get_host()
            if self.request.is_secure():
                return '%s://%s%s' % ('https', url, rev)
            else:
                return '%s://%s%s' % ('http', url, rev)
        else:
            return rev

    def check_valid_zone(self, zone, strict_owner=True):
        try:
            args = {'id': int(zone)}
        except:
            args = {'zone_name': zone}
        try:
            if self.account.is_staff or self.account.is_superuser:
                hasZone = dnsZones.objects.get(**args)
            else:
                hasZone = dnsZones.objects.get(owner=self.account, **args)
        except:
            if strict_owner is False:
                try:
                    z = dnsZones.objects.get(**args)
                    ZoneShares.objects.get(zone=z, user=self.account)
                    hasZone = z
                except:
                    raise NotFound('Zone %s does not exist.' % zone)
            else:
                raise NotFound('Zone does not exist')

        dnsObject = DnsRecords.objects.filter(zone=hasZone.zone_name)

        if dnsObject.count() == 0:
            raise NotFound('Zone is missing from dns records. Please contact technical support')

        return hasZone

    @transaction.commit_on_success(using='default')
    def share(self, zone, user):
        z = self.check_valid_zone(zone)
        if type(user) is list:
            for i in user:
                try:
                    usr = User.objects.get(username=str(i))
                except:
                    raise NotFound("The user you are trying to share this zone with does not exist")
                d = ZoneShares.objects.filter(zone=z, user=usr)
                if d.count() > 0:
                    raise DuplicateEntry("This zone is already shared with that user")
                try:
                    ZoneShares.objects.create(zone=z, user=usr)
                except:
                    raise Exception("Failed to share zone. Please contact technical support.")
        else:
            try:
                usr = User.objects.get(username=str(user))
            except:
                raise NotFound("The user you are trying to share this zone with does not exist")

            d = ZoneShares.objects.filter(zone=z, user=usr)
            if d.count() > 0:
                raise DuplicateEntry("This zone is already shared with that user")

            try:
                ZoneShares.objects.create(zone=z, user=usr)
            except:
                raise Exception("Failed to share zone. Please contact technical support.")
        return True

    @transaction.commit_on_success(using='default')
    def unshare(self, zone, user):
        z = self.check_valid_zone(zone)
        if type(user) is list:
            for i in user:
                if i.isdigit() is False:
                    try:
                        usr = User.objects.get(username=str(i))
                    except:
                        raise ValueError("The user you are trying to unshare this zone with does not exist")
                    d = ZoneShares.objects.filter(zone=z, user=usr)
                else:
                    usr = int(i)
                    d = ZoneShares.objects.filter(zone=z, id=usr)

                if d.count() > 0:
                    d.delete()
                else:
                    raise NotFound("This zone is not shared with that user")
        else:
            if user.isdigit() is False:
                try:
                    usr = User.objects.get(username=str(user))
                except:
                    raise ValueError("The user you are trying to unshare this zone with does not exist")
                d = ZoneShares.objects.filter(zone=z, user=usr)
            else:
                usr = int(user)
                d = ZoneShares.objects.filter(zone=z, id=usr)
            if d.count() > 0:
                d.delete()
            else:
                raise NotFound("This zone is not shared with that user")
        return True

    def share_as_dict(self, share):
        tmp = {
            'username': share.user.username,
            'first_name': share.user.first_name,
            'last_name': share.user.last_name,
            'id': share.id,
            'url': self.build_full_url(
                reverse(
                    '%s_share_reg' % self.rev_prefix,
                    args=(share.zone.id, share.id, self.format)
                )
            )
        }
        return tmp

    def list_shares(self, zone=None, reg_id=None):
        if zone is None:
            zones = dnsZones.objects.filter(owner=self.account)
            tmp = {}
            for i in zones:
                shares = ZoneShares.objects.filter(zone=i)
                tmp[str(i.zone_name)] = [{
                    'username': j.user.username,
                    'first_name': j.user.first_name,
                    'last_name': j.user.last_name,
                    'id': j.id,
                    'url': self.build_full_url(
                        reverse(
                            '%s_share_reg' % self.rev_prefix,
                            args=(i.id, j.id, self.format)
                        )
                    )
                } for j in shares]
        else:
            zoneObj = self.check_valid_zone(zone)
            if reg_id:
                try:
                    args = {'id': int(reg_id)}
                except:
                    args = {'user__username': str(reg_id)}
            else:
                args = {}
            shares = ZoneShares.objects.filter(zone=zoneObj, **args)
            tmp = []
            for i in shares:
                tmp.append(self.share_as_dict(i))
        return tmp

    def listZones(self, strip_type=False):
        tmp = [[], [], []]
        zones = dnsZones.objects.filter(owner=self.account)
        shared = ZoneShares.objects.filter(user=self.account)
        for i in zones:
            is_shared = ZoneShares.objects.filter(zone=i).count() > 0
            if is_shared is True:
                d_type = 'shared_dom owned_dom'
            else:
                d_type = 'owned_dom'

            rev = reverse('%s' % self.rev_prefix, args=(i.id, self.format))
            rev_shares = reverse('%s_shares' % self.rev_prefix, args=(i.id, self.format))
            dom_reg = {
                'zone_name': i.zone_name,
                'add_date': i.add_date,
                'last_update': i.last_update,
                'owned': True,
                'shared': is_shared,
                'url': self.build_full_url(rev),
                'shared_with': [
                    {
                        "username": j.user.username,
                        "first_name": j.user.first_name,
                        "last_name": j.user.last_name,
                        "url": self.build_full_url(rev_shares),
                    } for j in i.zoneshares_set.filter()],
                'type': d_type,
                'id': i.id,
            }
            if strip_type:
                del dom_reg['type']
            tmp[0].append(dom_reg)

        for i in shared:
            rev = reverse('%s' % self.rev_prefix, args=(i.zone.id, self.format))
            dom_reg = {
                'zone_name': i.zone.zone_name,
                'add_date': i.zone.add_date,
                'last_update': i.zone.last_update,
                'owned': False,
                'shared': False,
                'url': self.build_full_url(rev),
                'owned_by': {
                    'username': i.zone.owner.username,
                    'last_name': i.zone.owner.last_name,
                    'first_name': i.zone.owner.first_name,
                },
                'type': 'shared_dom',
                'id': i.id,
            }
            if strip_type:
                del dom_reg['type']
            tmp[1].append(dom_reg)
        # tmp[0] = sorted(tmp[0], key=lambda k: k['zone_name'])
        # tmp[1] = sorted(tmp[1], key=lambda k: k['zone_name'])
        tmp[2].extend(tmp[0])
        tmp[2].extend(tmp[1])
        # tmp[2] = sorted(tmp[2], key=lambda k: k['zone_name'])
        return tmp

    def record_as_dict(self, record=None):
        if record is None:
            raise NotFound('No DNS record was selected')
        tmp = {}
        for i in validators.recordTypes[record.type]:
            tmp[i] = getattr(record, i)
            tmp['id'] = record.id

        return tmp

    def getRecord(self, zone=None, recordID=None):
        if zone is None:
            raise NotFound('No zone was selected')
        z = self.check_valid_zone(zone, strict_owner=False)
        zone_name = z.zone_name
        if recordID is None:
            raise ValueError('No record was specified')
        try:
            r = int(recordID)
        except:
            raise InvalidId('Invalid record ID %r' % recordID)
        try:
            self.record = DnsRecords.objects.get(zone=zone_name, id=r)
        except Exception:
            raise NotFound('No such record')

        rec = self.record_as_dict(record=self.record)
        rev = reverse(
            '%s_record' % self.rev_prefix,
            args=(self.record.zone, self.record.id, self.format)
        )
        rec['url'] = self.build_full_url(rev)
        return rec

    def clean_records(self, data):
        # compatibility
        if 'entries' in data:
            data = data['entries']
        tmp = []
        if type(data) is dict:
            tmp.append(data)
            return tmp
        return data

    def zoneEntries_as_dict(self, zone, strip_id=False):
        z = self.check_valid_zone(zone, strict_owner=False)
        dnsObject = DnsRecords.objects.filter(zone=str(z.zone_name))

        if dnsObject.count() == 0:
            raise NotFound('Zone is missing from dns records. Please contact technical support')

        records = []
        for i in dnsObject:
            x = {}
            if i.type in validators.recordTypes:
                if strip_id is False:
                    x['id'] = i.id
                for j in validators.recordTypes[i.type]:
                    x[j] = getattr(i, j)
                rev = reverse('%s_record' % self.rev_prefix, args=(z.id, i.id, self.format))
                x['url'] = self.build_full_url(rev)
                records.append(x)
            else:
                pass
        return records

    def bulk_zones_as_list(self, zones=None, strip_id=True):
        clean_zones = {}
        if zones:
            if type(zones) is not list:
                raise ValueError('Invalid input')
        else:
            zones_q = dnsZones.objects.filter(owner=self.account)
            zones = []
            for i in zones_q:
                zones.append(i.zone_name)

        for i in zones:
            tmp = self.zoneEntries_as_dict(i, strip_id)
            clean_zones[i] = tmp

        return clean_zones

    def update_SOA_serial(self, old_serial):
        today = str(date.today().strftime("%Y%m%d"))
        serial = str(old_serial)
        if serial.startswith(today):
            if serial.endswith('99'):
                serial = str(today) + "00"
            else:
                serial = str(int(serial) + 1)

        return int(serial)

    def count_new_records(self, data):
        count = 0
        for i in data:
            if 'id' not in i:
                count += 1
        return count

    @transaction.commit_on_success(using='bind')
    def updateRecords(self, zone, data):
        record_ids = []
        zoneObject = self.check_valid_zone(zone, strict_owner=False)
        data = self.clean_records(data)

        all_rec = DnsRecords.objects.filter(zone=zoneObject.zone_name)

        # Needed for partial record update.
        for i in data:
            if 'id' in i and i['id'] is not None:
                found = False
                for j in all_rec:
                    if int(i['id']) == int(j.id):
                        if 'type' not in i:
                            i['type'] = j.type
                        found = True
                        break
                if found is False:
                    raise NotFound('One of the records submited could not be found. Please make sure nobody esle is editing this zone.')

        # Validam inregistrarile. Se scoate SOA daca a fost trimis
        # se valideaza inregistrarile, si se pune un ttl minim
        # de 600 (10 min) daca cel trimis e mai mic.
        cleaned_records = validators.ValidateRecords(data).cleaned_data()
        # obey max records
        curent_record_count = all_rec.count()
        new_record_count = curent_record_count + self.count_new_records(data)
        zone_max_records = functions.getMaxRecords(zoneObject)
        if new_record_count > zone_max_records:
            raise NotAllowed('You have reached the maximum number of records for this zone.')

        # update SOA serial
        try:
            # Preluam SOA, modificam si salvam serial
            SOA = DnsRecords.objects.get(zone=str(zone), type='SOA')
            SOA.serial = int(self.update_SOA_serial(SOA.serial))
            SOA.save()
        except:
            # SOA este invalida, stergem SOA si adaugam o inregistrare valida
            DnsRecords.objects.filter(zone=str(zone), type='SOA').delete()
            soa_data = self.generate_SOA()
            soa_data['zone'] = zone
            try:
                DnsRecords.objects.create(**soa_data)
            except:
                raise Exception('Failed to create SOA record.')
        # END SOA update
        for i in cleaned_records:
            for j in i.keys():
                if j not in validators.recordTypes[i['type']] and str(j) != 'id':
                    del i[j]
            # compatibillity for site access and API access
            # actualizarea unei zone din site va adauga campul ID automat,
            # insa daca e vb de o inregistrare noua, 'id' va fi none. Prin API
            # campul 'id' va lipsi. Il adaugam aici pentru a pastra compatibilitatea
            if 'id' not in i:
                i['id'] = None

            if i['id'] is not None:
                try:
                    r = DnsRecords.objects.get(id=i['id'])
                    for j in i.keys():
                        setattr(r, j, i[j])
                    r.save()
                except Exception:
                    raise Exception("Failed to update record. Please contact technical support.")
            else:
                i['zone'] = zoneObject.zone_name
                x = DnsRecords.objects.create(**i)
                record_ids.append(x.id)
        return record_ids

    def generate_SOA(self):
        # nu uita sa adaugi si "zone" inainte de create/update
        resp_person = getattr(s, 'DNS_RESP_PERSON', 'support.enabledns.com')
        soa_data = getattr(s, 'DNS_SOA_DATA', 'ns.enabledns.com.')
        serial = str(date.today().strftime("%Y%m%d")) + "00"
        data = {
            'retry': 7200,
            'type': 'SOA',
            'minimum': 600,
            'refresh': 14400,
            'host': '@',
            'expire': 1209600,
            'ttl': 1,
            'serial': serial,
            'data': soa_data,
            'resp_person': resp_person,
        }
        return data

    @transaction.commit_on_success
    @transaction.commit_on_success(using='bind')
    def createZone(self, data):
        if type(data) is not dict:
            raise ValueError('Input data must be of type dict. Got %s' % type(data))

        # obey profile.maxDoms
        current_zones = dnsZones.objects.filter(owner=self.account).count()
        estimated_zones = int(len(data.keys())) + int(current_zones)
        if int(estimated_zones) > int(self.profile.maxDoms):
            raise NotAllowed('You have reached your domain limit. Please contact technical support for more information.')

        for i in data.keys():
            zone_name = i
            r = re.compile('^([a-zA-Z0-9-]{,63}\.){1,}[a-zA-Z0-9-]{,63}$')
            if not r.match(zone_name):
                raise ValueError('Invalid zone name.')
            zone_data = data[i]

            if type(zone_data) is not list:
                raise ValueError('Invalid data for zone')

            # obey profile.global_records_per_zone
            if int(len(zone_data)) > self.profile.global_records_per_zone:
                raise NotAllowed('You have exceeded the maximum number of records for this zone')

            # check if zone exists in zones table
            ZoneName = dnsZones.objects.filter(zone_name=zone_name)
            if ZoneName.count() > 0:
                raise DuplicateEntry('Zone already exists')

            #check if zone exists in bind database
            a = DnsRecords.objects.filter(zone=zone_name)
            if a.count() > 0:
                raise DuplicateEntry('A DNS zone with that name already exists.')

            # clean zone data
            cleaned_data = validators.ValidateRecords(zone_data).cleaned_data()

            # add SOA
            found = False
            for i in cleaned_data:
                if str(i['type']).lower() == 'soa':
                    i = self.generate_SOA()
                    found = True
            if found is False:
                cleaned_data.append(self.generate_SOA())
            #END soa

            # Add zone to bind database
            ent = []
            for i in cleaned_data:
                i['zone'] = zone_name
                ent.append(DnsRecords(**i))
            DnsRecords.objects.bulk_create(ent)

            # Add zone to enableDNS database
            self.zone = dnsZones.objects.create(zone_name=zone_name, owner=self.account)
        return True

    @transaction.commit_on_success(using='bind')
    def deleteRecord(self, zone=None, recordID=None):
        if zone is None:
            raise NotFound('No zone was selected')
        else:
            zoneObject = self.check_valid_zone(zone, strict_owner=False)
            zone_name = zoneObject.zone_name

        if recordID is None:
            raise ValueError('No record was specified')
        else:
            if type(recordID) is list:
                for i in recordID:
                    try:
                        record = DnsRecords.objects.get(zone=zone_name, id=i)
                    except:
                        raise NotFound('Record does not exist')
                    if record.type != 'SOA':
                        record.delete()
                    else:
                        raise NotAllowed('The SOA record may not be deleted')
            else:
                try:
                    record = DnsRecords.objects.get(zone=zone_name, id=recordID)
                except Exception:
                    raise NotFound('Record does not exist')
                if record.type != 'SOA':
                    record.delete()
                else:
                    raise NotAllowed('The SOA record may not be deleted')

        # update SOA serial
        try:
            # Preluam SOA, modificam si salvam serial
            SOA = DnsRecords.objects.get(zone=str(zone), type='SOA')
            SOA.serial = int(self.update_SOA_serial(zone))
            SOA.save()
        except:
            # SOA este invalida, stergem SOA si adaugam o inregistrare valida
            DnsRecords.objects.filter(zone=str(zone), type='SOA').delete()
            data = self.generate_SOA()
            data['zone'] = zone
            try:
                DnsRecords.objects.create(**data)
            except:
                raise Exception('Failed to create SOA record for zone.')
        # END SOA update

        return True

    def process_zone_array(self, zones):
        clean_zones = {'owned': [], 'shared': []}
        if type(zones) is list:
            for i in zones:
                try:
                    args = {'id': int(i)}
                except:
                    args = {'zone_name': str(i)}
                try:
                    zone_obj = dnsZones.objects.get(owner=self.account, **args)
                    clean_zones['owned'].append(zone_obj)
                except:
                    try:
                        zone_obj = dnsZones.objects.get(**args)
                        zone_shr = ZoneShares.objects.get(zone=zone_obj, user=self.account)
                        clean_zones['shared'].append(zone_shr)
                    except:
                        raise NotFound('Zone %s does not exist. If this is an error, please contact technical support' % i)
        else:
            try:
                args = {'id': int(zones)}
            except:
                args = {'zone_name': str(zones)}
            try:
                zone_obj = dnsZones.objects.get(owner=self.account, **args)
                clean_zones['owned'].append(zone_obj)
            except:
                try:
                    zone_shr = ZoneShares.objects.get(zone__zone_name=str(zones), user=self.account)
                    clean_zones['shared'].append(zone_shr)
                except:
                    raise NotFound('Zone %s does not exist. If this is an error, please contact technical support' % zones)
        return clean_zones

    @transaction.commit_on_success
    @transaction.commit_on_success(using='bind')
    def deleteZone(self, zone=None):
        if zone is None:
            raise NotFound('No zone was selected')
        else:
            zones = self.process_zone_array(zone)

        for i in zones['owned']:
            dnsObj = DnsRecords.objects.filter(zone=str(i.zone_name))
            if dnsObj.count() > 0:
                dnsObj.delete()
            i.delete()

        for j in zones['shared']:
            j.delete()
        return True
