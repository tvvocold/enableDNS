import base64
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate, login

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps


# cherry picked from:
# http://code.google.com/p/django-httpbasicauth/source/browse/trunk/django-httpbasicauth/django_httpbasicauth/decorators.py
def basic_auth(func):
    @wraps(func)
    def wrapper(request, *args, **kw):
        if request.user.is_authenticated():
            return func(request, *args, **kw)
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) != 2:
                return HttpResponseBadRequest()

            auth_type, auth_data = auth
            if auth_type.lower() != "basic":
                return HttpResponseBadRequest()

            try:
                uname, passwd = base64.b64decode(auth_data).split(':')
            except:
                return HttpResponseBadRequest()

            user = authenticate(username=uname, password=passwd)
            if user:
                if user.is_active:
                    login(request, user)
                    request.user = user
                    return func(request, *args, **kw)

        response = HttpResponse("Unauthorized")
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="EnableDNS"'
        return response
    return wrapper
