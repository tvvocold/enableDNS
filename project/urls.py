from django.conf.urls import *

import project.stats.views as stat_views
import project.backend.views as backend_views
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api', include('project.api.urls')),
    url(r'^ip[/]?$', backend_views.getIP),
    url(r'^stats[/]?$', stat_views.statistics),
    url(r'^nic/update[/]?', backend_views.update_ip, name="dynamic_update"),

    # Catch all
    url(r'^(.*)$', lambda x, y: HttpResponseRedirect(reverse('index', args=('api',)))),
)
