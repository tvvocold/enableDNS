from project.backend.models import *
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import RequestContext


def get_stats():
    users = User.objects.filter(is_active=True).count()
    zones = dnsZones.objects.filter().count()
    records = DnsRecords.objects.filter().count()
    return (
        'stats.html',
        {'users': users, 'zones': zones, 'records': records}
    )


@login_required
def statistics(request):
    if request.user.is_staff is True or request.user.is_superuser is True:
        vals = get_stats()
        return render_to_response(*vals, context_instance=RequestContext(request))

    return render_to_response(
        'stats.html',
        {
            'err': 'Access denied',
        },
        context_instance=RequestContext(request)
    )
