from django.db import transaction
from django.contrib.auth.models import User
from django.db.models import Q
from project.backend.models import *
from project.backend.Exceptions import *
import project.backend.validators as validators
import project.backend.dnsOperations as op
import json
from django.core.urlresolvers import reverse


class Templates(object):

    def __init__(self, user, request=None, rev_prefix=None, format=None):
        if isinstance(user, User) is False:
            raise Exception('Expected User object')
        self.account = user
        self.profile = user.get_profile()
        self.request = request
        self.z = op.Zone(self.account)
        self.rev_prefix = rev_prefix or 'v1_0'
        self.format = format or 'json'

    @transaction.commit_on_success(using='default')
    def create(self, data):
        required_keys = ('name', 'data',)
        for i in required_keys:
            if i not in data:
                raise ValueError("Missing %s key" % i)

        name = data['name']

        tpl = ServiceTemplates.objects.filter(name=str(name), owner=self.account)
        if tpl.count() > 0:
            raise ValueError('A template with that name already exists.')
        cleaned_data = validators.ValidateRecords(data['data']).cleaned_data()
        try:
            tmp = ServiceTemplates.objects.create(owner=self.account, name=str(name), data=json.dumps(cleaned_data))
        except:
            raise Exception('Failed to add template to database')
        return tmp

    def build_full_url(self, rev):
        if self.request:
            url = self.request.get_host()
            if self.request.is_secure():
                return '%s://%s%s' % ('https', url, rev)
            else:
                return '%s://%s%s' % ('http', url, rev)
        else:
            return rev

    @transaction.commit_on_success(using='default')
    def deleteTemplate(self, ids):
        if type(ids) is not list:
            ids = [ids, ]
        try:
            ids = [int(i) for i in ids]
        except:
            raise ValueError("Template ids must be integers")

        tpl = ServiceTemplates.objects.filter(id__in=ids, owner=self.account)
        if tpl.count() == 0:
            raise NotFound("No templates matching your querie were found.")
        for i in tpl:
            if i.zoneservices_set.filter().count() > 0:
                raise Exception('Template %s is in use.' % i.name)
        tpl.delete()
        return True

    @transaction.commit_on_success(using='default')
    def update(self, tpl_id, data):
        try:
            tpl_id = int(tpl_id)
        except:
            raise ValueError("Template id must be integer")
        try:
            tpl = ServiceTemplates.objects.get(pk=tpl_id, owner=self.account)
        except:
            raise NotFound("No such template")

        allowed_fields = ("name", "data",)
        for i in data.keys():
            if i not in allowed_fields:
                del data[i]

        if data.get("data"):
            data["data"] = json.dumps(validators.ValidateRecords(data["data"]).cleaned_data())

        for i in data.keys():
            setattr(tpl, i, data[i])
        tpl.save()
        return True

    def listZoneTemplates(self, zone, template=None):
        zone_obj = self.z.check_valid_zone(zone, strict_owner=False)
        if template:
            try:
                tpl = zone_obj.zoneservices_set.get(pk=int(template))
            except:
                raise NotFound("No such template associated")
            return {
                'id': tpl.id,
                'name': tpl.template.name,
                'url': self.build_full_url(
                    reverse(
                        "%s_domain_template" % self.rev_prefix,
                        args=(zone_obj.id, tpl.id, self.format)
                    )
                ),
                'template_url': self.build_full_url(
                    reverse(
                        "%s_templates" % self.rev_prefix,
                        args=(tpl.template.id, self.format)
                    )
                ),
            }
        return [
            {
                'id': i.id,
                'name': i.template.name,
                'url': self.build_full_url(
                    reverse(
                        "%s_domain_template" % self.rev_prefix,
                        args=(zone_obj.id, i.id, self.format)
                    )
                ),
                'template_url': self.build_full_url(
                    reverse(
                        "%s_templates" % self.rev_prefix,
                        args=(i.template.id, self.format)
                    )
                ),
            } for i in zone_obj.zoneservices_set.filter()]

    @transaction.commit_on_success(using='default')
    def addTemplate(self, zone, template):
        try:
            template = int(template)
        except:
            raise ValueError("Template Id must be integer")
        zone_obj = self.z.check_valid_zone(zone, strict_owner=False)
        # get template data
        try:
            tpl = ServiceTemplates.objects.get(pk=template)
        except:
            raise ValueError('No such template')

        try:
            has_tpl = ZoneServices.objects.get(zone_name=zone_obj, template=tpl)
        except:
            has_tpl = None

        if has_tpl:
            raise ValueError('Template is already applied')

        try:
            records = json.loads(str(tpl.data))
        except:
            raise ValueError('Invalid template data. Please contact technical support.')

        ids = self.z.updateRecords(zone, records)
        ZoneServices.objects.create(zone_name=zone_obj, template=tpl, record_ids=json.dumps(ids))
        return True

    @transaction.commit_on_success(using='bind')
    @transaction.commit_on_success(using='default')
    def removeTemplate(self, zone, template):
        zone_obj = self.z.check_valid_zone(zone, strict_owner=False)
        try:
            zone_tpl = ZoneServices.objects.get(zone_name=zone_obj, id=int(template))
        except:
            raise ValueError('Zone does not have this template applied.')

        try:
            ids = json.loads(zone_tpl.record_ids)
        except:
            raise ValueError('Invalid record data. Please contact technical support.')

        try:
            DnsRecords.objects.filter(id__in=ids, zone=str(zone_obj.zone_name)).delete()
        except:
            pass
        zone_tpl.delete()
        return True

    def listTemplates(self, tpl_id=None):
        args = {}
        if tpl_id:
            try:
                args = {'id': int(tpl_id)}
            except:
                raise ValueError('Invalid template id')
        tp = ServiceTemplates.objects.filter(Q(owner=self.account) | Q(owner=None), **args)
        if tpl_id:
            if tp.count() == 0:
                raise NotFound("No such template")
            return {
                "name": tp[0].name,
                "data": json.loads(tp[0].data),
                "id": tp[0].id,
                "global": tp[0].owner is None,
                "url": self.build_full_url(reverse("%s_templates" % self.rev_prefix, args=(tp[0].id, self.format)))
            }
        return [
            {
                "name": i.name,
                "data": json.loads(i.data),
                "id": i.id,
                "global": i.owner is None,
                "url": self.build_full_url(reverse("%s_templates" % self.rev_prefix, args=(i.id, self.format)))
            } for i in tp]

    def isAvailable(self, template, skip_global=False):
        args = []
        if skip_global is True:
            args.append(~Q(owner=None))
        tp = ServiceTemplates.objects.filter(*args, id=int(template))
        if tp.count() == 1:
            return True
        return False
