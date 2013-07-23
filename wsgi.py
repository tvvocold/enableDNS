import os, sys

# Set up environment
############################################################

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'

#END########################################################

import django.core.handlers.wsgi

os.environ['HTTPS'] = "on"

application = django.core.handlers.wsgi.WSGIHandler()
