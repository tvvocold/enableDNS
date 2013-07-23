from django.http import HttpResponse
from project.backend.decorators import basic_auth
from project.backend.models import *
import project.backend.dnsOperations as op
import project.backend.functions as func


def getIP(request):
    return HttpResponse(request.META['REMOTE_ADDR'])


@basic_auth
def update_ip(request):
    myip = request.GET.get('myip', request.META['REMOTE_ADDR'])
    if func.validIP(myip) is False:
        myip = request.META['REMOTE_ADDR']

    hostname = request.GET.get('hostname')

    obj = op.Zone(request.user, request)

    if not hostname:
        return HttpResponse("nofqdn")

    try:
        hosts = [int(i) for i in hostname.split(',')]
    except:
        return HttpResponse("notfqdn")

    if len(hosts) > 20:
        return HttpResponse("numhost")

    records = DnsRecords.objects.filter(id__in=hosts, type="A")
    if records.count() == 0:
        return HttpResponse("nohost")

    zones = records.values_list('zone', flat=True).distinct()
    for i in zones:
        try:
            obj.check_valid_zone(i, strict_owner=False)
        except:
            return HttpResponse("nohost")

    records.update(data=str(myip))
    return HttpResponse("good")
