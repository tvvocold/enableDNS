from django.conf.urls import patterns, url
import project.api.v1_0.views as views
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import *


urlpatterns = patterns(
    '',
    url(r'^/shares/(?P<zone_slug>[^/]+)$', views.ZoneSares.as_view(), name='v1_0_shares'),
    url(r'^/shares/(?P<zone_slug>[^/]+)/(?P<reg_slug>[^/]+)[/]?$', views.ZoneSares.as_view(), name='v1_0_share_reg'),
    url(r'^/shares[/]?$', views.ZoneSares.as_view(), name='v1_0_shares_index'),
    url(r'^/domains[/]?$', views.DomainsView.as_view(), name='v1_0_index'),
    url(r'^/domains/(?P<zone_slug>[^/]+)/templates/(?P<template>[^/]+)[/]?$', views.DomainTemplatesView.as_view(), name='v1_0_domain_template'),
    url(r'^/domains/(?P<zone_slug>[^/]+)/templates[/]?$', views.DomainTemplatesView.as_view(), name='v1_0_domain_template_index'),
    url(r'^/domains/(?P<zone_slug>[^/]+)[/]?$', views.DomainsView.as_view(), name='v1_0'),
    url(r'^/domains/(?P<zone_slug>[^/]+)/(?P<reg_slug>[0-9]+)[/]?$', views.DomainsView.as_view(), name='v1_0_record'),
    url(r'^/templates/(?P<template>[^/]+)$', views.TemplatesView.as_view(), name='v1_0_templates'),
    url(r'^/templates[/]?$', views.TemplatesView.as_view(), name='v1_0_templates_index'),
    url(r'^[/]?$', views.IndexView.as_view(), name='index'),
)

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html', 'yaml', 'api'], suffix_required=True)

urlpatterns += patterns(
    '',
    url(r'^/v1.0', include('project.api.v1_0.urls')),
    url(r'^/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
