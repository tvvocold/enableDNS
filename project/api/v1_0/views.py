from rest_framework.response import Response
from project.backend.Exceptions import *
from rest_framework.views import View, APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings as s
import project.backend.dnsOperations as op
import project.backend.Templates as Templates
from django.core.urlresolvers import reverse
from rest_framework.exceptions import *

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps


def process_err(func):
    @wraps(func)
    def cleaned_function(self, request, *args, **kwargs):
        profile = request.user.get_profile()
        if profile.has_api is False:
            return Response({"detail": "You are not allowed to access the API. Please contact technical support."}, 401)
        try:
            return func(self, request, *args, **kwargs)
        except ValueError as err:
            return Response({"detail": str(err)}, status=400)
        except NotFound as err:
            return Response({"detail": str(err)}, status=404)
        except NotAllowed as err:
            return Response({"detail": str(err)}, status=401)
        except DuplicateEntry as err:
            return Response({"detail": str(err)}, status=409)
        except APIException as err:
            return Response({"detail": err.detail}, status=err.status_code)
        except Exception as err:
            return Response({"detail": str(err)}, status=500)
    return cleaned_function


class ResourceNotFound(View):
    def read(self, request, *args, **kw):
        return Response({"detail": str(err)}, status=404)

    def delete(self, request, *args, **kw):
        return Response({"detail": str(err)}, status=404)

    def create(self, request, *args, **kw):
        return Response({"detail": str(err)}, status=404)

    def update(self, request, *args, **kw):
        return Response({"detail": str(err)}, status=404)


class IndexView(APIView):
    """
    Overview of API resources
    """
    permissions = (IsAuthenticated,)

    def build_full_url(self, rev):
        url = self.request.get_host()
        if self.request.is_secure():
            return '%s://%s%s' % ('https', url, rev)
        else:
            return '%s://%s%s' % ('http', url, rev)

    def get(self, request, format=None):
        format = format or 'json'
        ret = [
            {
                "ResourceName": "domains",
                "url": self.build_full_url(reverse('v1_0_index', args=(format,)),)
            },
            {
                "ResourceName": "shares",
                "url": self.build_full_url(reverse('v1_0_shares_index', args=(format,)),)
            },
            {
                "ResourceName": "templates",
                "url": self.build_full_url(reverse('v1_0_templates_index', args=(format,)),)
            },
        ]
        response = Response(ret, status=200)
        return response


class DomainsView(APIView):
    """
    These are all the domains you have added to your account. Here you may add,
    remove or update a domain. You may also update individual records for a
    specific domain. Bellow, are a few examples on how you may acomplish this.

    ## Add a new zone

    When adding a new domain using the enableDNS web page, you are required to
    specify only the domain name. A DNS zone is created automatically from a
    predefined template. With the API you have the freedom to choose which
    records get created. For example, you may wish to only have
    one A record and no other records. Thats easely accomplished with a simple
    POST to the API

        {
          "example.com":
            [
              {
                "type": "A",
                "host":"@",
                "data":"192.168.1.1",
                "ttl":"3600"
              }
            ]
        }

    Adding multiple domains is also supported:

        {
          "example.com":
            [
              {
                "type": "A",
                "host":"@",
                "data":"192.168.1.1",
                "ttl":"3600"
              }
            ],
            "example2.com":
            [
              {
                "type": "A",
                "host":"@",
                "data":"192.168.1.1",
                "ttl":"3600"
              }
            ]
        }

    ## Add new record to zone

        GET /api/domains/[ZONE NAME].api

    Adding new records can be done in the same manner in which you add a new domain.
    You may add multiple records to the same zone.

        [
          {
            "type": "A",
            "host":"mail",
            "data":"192.168.1.1",
            "ttl":"3600" 
          },
          {
            "type": "MX",
            "host":"@",
            "data":"mail",
            "priority": 0,
            "ttl":"3600"
          }
        ]

    The above example will add 2 records:

      * An A record (mail.example.com) pointed to 192.168.1.1
      * An MX record that points example.com to mail.example.com (the previous A record)

    ## Updating a zone

    There are very few differences between create (POST) and update (PUT). They work almost
    the same way, with the only difference that when updating a record you have to specify
    the record ID inside the record block.

        [
          {
            "id": 390,
            "type": "A",
            "host": "mail",
            "data":"192.168.1.1",
            "ttl":"3600"
          }
        ]

      * Note the extra 'id' field inside the json
      * This will update the record with id 390 in zone example.com

    In the case of updates, you may also specify only the information you wish to change.
    For example, if you only need to update the IP address for hostname mail.example.com,
    the following is enought:

        [
          {
            "id": 390,
            "data": "192.168.1.2"
          }
        ]

    ## Mixing it up

    Now, because there are so few differences between the two methods (POST and PUT) we
    allow updating and creating of new records using any of those verbs. This is not verry
    REST-ful but at least this way you can update and create records using one API call.
    As a result, you can POST or PUT a json with an existing record and a new record.
    Here is an example of mixing updates with creating new records:

        [
          {
            "id": 390 ,
            "type": "A",
            "host":"mail",
            "data":"192.168.1.1",
            "ttl":"3600"
          },
          {
            "type": "A",
            "host":"ftp",
            "data":"192.168.1.1",
            "ttl":"3600"
          }
        ]

    Two things are happening here:

      * The record with id 390 is being updated
      * A new A record (ftp.example.com) is being created

    ## Deleting a zone or record

    To delete a zone or a record, all you need to do is send a request using the DELETE verb
    to the URL you want to delete. Every zone or record has a "url" field inside. Send a DELETE
    to that URL and the record will be deleted.
    """
    permission_classes = (IsAuthenticated,)

    @process_err
    def get(self, request, zone_slug=None, reg_slug=None, format=None):
        obj = op.Zone(request.user, request, rev_prefix='v1_0', format=format)
        if zone_slug is None:
            res = obj.listZones(strip_type=True)[2]
            return Response({"results": res}, status=200)
        if reg_slug is None:
            res = obj.zoneEntries_as_dict(zone_slug)
            return Response(res, status=200)
        res = obj.getRecord(zone=zone_slug, recordID=reg_slug)
        return Response(res, status=200)

    @process_err
    def post(self, request, zone_slug=None, reg_slug=None, format=None):
        obj = op.Zone(request.user, request, rev_prefix='v1_0', format=format)
        if request.DATA:
            data = request.DATA
        else:
            raise ValueError("No post data received")
        if zone_slug is None:
            obj.createZone(data)
        else:
            obj.updateRecords(zone_slug, data)
        return Response({"detail": "success"}, status=201)

    @process_err
    def put(self, request, zone_slug, reg_slug=None, format=None):
        obj = op.Zone(request.user, request, rev_prefix='v1_0', format=format)
        if request.DATA:
            data = request.DATA
        else:
            raise ValueError("No post data received")
        if reg_slug:
            return Response({"detail": "Please refer to %s for instructions on how to update individual records." % s.DEV_HELP_URL}, 401)
        obj.updateRecords(zone_slug, data)
        return Response({"detail": "success"}, status=200)

    @process_err
    def delete(self, request, zone_slug=None, reg_slug=None, format=None):
        obj = op.Zone(request.user, request, rev_prefix='v1_0', format=format)
        if zone_slug is None:
            if 'zones' in request.GET:
                zones_arr = request.GET['zones'].split(',')
                obj.deleteZone(zone=zones_arr)
                return Response({}, status=204)
            else:
                raise ValueError()

        if reg_slug is None:
            if 'ids' in request.GET:
                ids_arr = request.GET['ids'].split(',')
                obj.deleteRecord(recordID=ids_arr, zone=zone_slug)
                return Response({}, status=204)
            obj.deleteZone(zone_slug)
            return Response({}, status=204)
        obj.deleteRecord(recordID=reg_slug, zone=zone_slug)
        return Response({}, status=204)


class TemplatesView(APIView):

    permission_classes = (IsAuthenticated,)

    @process_err
    def get(self, request, template=None, format=None):
        obj = Templates.Templates(request.user, request=request, rev_prefix='v1_0', format=format)
        rsp = obj.listTemplates(tpl_id=template)
        return Response({"results": rsp}, status=200)

    @process_err
    def post(self, request, template=None, format=None):
        obj = Templates.Templates(request.user, request=request)
        if request.DATA:
            data = request.DATA
        else:
            raise ValueError("No post data received")
        obj.create(data)
        return Response({"detail": "success"}, status=201)

    @process_err
    def delete(self, request, template, format=None):
        obj = Templates.Templates(request.user, request=request)
        obj.deleteTemplate(template)
        return Response({}, status=204)

    @process_err
    def put(self, request, template=None, format=None):
        obj = Templates.Templates(request.user, request=request)
        if request.DATA:
            data = request.DATA
        else:
            raise ValueError("No post data received")

        obj.update(template, data)
        return Response({"detail": "success"}, status=200)


class DomainTemplatesView(APIView):

    permission_classes = (IsAuthenticated,)

    @process_err
    def get(self, request, zone_slug, template=None, format=None):
        obj = Templates.Templates(request.user, request=request, rev_prefix='v1_0', format=format)
        return Response(obj.listZoneTemplates(zone_slug, template=template), status=200)

    @process_err
    def post(self, request, zone_slug, template=None, format=None):
        obj = Templates.Templates(request.user, request=request)
        if template:
            raise ValueError("Invalid request")
        if request.DATA:
            data = request.DATA
        else:
            raise ValueError("No post data received")
        tpl_id = data['id']
        obj.addTemplate(zone_slug, tpl_id)
        return Response({"detail": "success"}, status=201)

    @process_err
    def delete(self, request, zone_slug, template=None, format=None):
        obj = Templates.Templates(request.user, request=request)
        obj.removeTemplate(zone_slug, template)
        return Response({}, status=204)


class ZoneSares(APIView):

    """
    Sharing is caring. To share a domain with one or more users you just need to POST
    an array of usernames to the API

    ## Add a share

    Please note, the users you want to add must already have an active account.

        [
            "example@example.com",
            "example2@example2.com"
        ]

    ## Removing a share

    As is the case with deleting a domain name, all you have to do is send a DELETE action to
    the coresponding URL of the share.
    """

    permission_classes = (IsAuthenticated,)

    @process_err
    def get(self, request, zone_slug=None, reg_slug=None, format=None):
        obj = op.Zone(request.user, request, rev_prefix='v1_0', format=format)
        shares = obj.list_shares(zone_slug, reg_slug)
        response = Response({"results": shares}, status=200)
        return response

    @process_err
    def delete(self, request, zone_slug=None, reg_slug=None, format=None):
        # reg_slug e userul
        obj = op.Zone(request.user, request, rev_prefix='v1_0', format=format)
        if reg_slug:
            obj.unshare(zone_slug, reg_slug)
        usrs = []
        if 'ids' in request.GET:
            usrs.extend(str(request.GET['ids']).split(','))
        if 'users' in request.GET:
            usrs.extend(str(request.GET['users']).split(','))
        obj.unshare(zone_slug, usrs)
        return Response({}, status=204)

    @process_err
    def post(self, request, zone_slug=None, reg_slug=None, format=None):
        if request.DATA:
            data = request.DATA
        else:
            raise ValueError("No post data received")

        obj = op.Zone(request.user, request, rev_prefix='v1_0', format=format)
        obj.share(zone_slug, data)
        return Response({"detail": "success"}, status=201)
