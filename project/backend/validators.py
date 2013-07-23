from project.backend.models import *
from project.backend.Exceptions import *
import project.backend.functions as func
import ipaddr as ip
import re


recordTypes = {
    'A': ['host', 'type', 'data', 'ttl'],
    'AAAA': ['host', 'type', 'data', 'ttl'],
    'MX': ['host', 'type', 'data', 'ttl', 'priority'],
    'NS': ['host', 'type', 'data', 'ttl'],
    'CNAME': ['host', 'type', 'data', 'ttl'],
    'SOA': ['host', 'type', 'data', 'ttl', 'refresh', 'retry', 'expire', 'minimum', 'serial', 'resp_person'],
    'TXT': ['host', 'type', 'data', 'ttl'],
    'PTR': ['host', 'type', 'data', 'ttl'],
    'SRV': ['host', 'type', 'data', 'ttl'],
}


class ValidateField(object):

    def __init__(self, data, strict_validation=True):
        if type(data) is not dict:
            raise ValueError("Invalid input")

        self.validated = {}
        for i in data.keys():
            meth = getattr(self, "validate_" % str(i), None)
            if strict_validation is True:
                if meth is None:
                    raise ValueError("No validation can be done for field of type %r" % i)
            else:
                # skip invalid fields
                continue
            self.validated[i] = meth(data[i])

    def validate_zone(self, val):
        return val


def validateField(key, value):
    if key == 'zone':
        s = str(value).split('.')
        if len(s) <= 1:
            raise Exception('Invalid zone name')
        for i in s:
            if len(i) > 64:
                return False
        return True

    if key == 'host':
        if str(value).endswith('.'):
            raise ValueError('Host fields must be relative. Values ending with dots are absolute.')
        s = str(value).split('.')
        if len(s) == 0:
            raise Exception('Invalid host field')

        for i in s:
            if len(i) > 64:
                return False
        return True

    if key == 'type':
        if str(value) not in recordTypes:
            return False
        return True

    int_fields = ['refresh', 'retry', 'expire', 'minimum', 'serial', 'priority', 'ttl']
    if key in int_fields:
        try:
            int(value)
        except:
            return False
        return True
    return True


class ValidateRecords(object):
    user = None

    def __init__(self, data=None):
        if data is None:
            raise ValueError('you must input a dictionary to verify')
        if type(data) is not dict and type(data) is not list:
            raise ValueError('Input data must be of type list')

        self.data = data
        self.cleaned = []

        self.fields = {"ttl": self.validate_ttl, "type": self.validate_type, "id": self.validate_id}

        for i in self.data:
            if 'type' not in i:
                raise ValueError('Invalid record data. Missing type field')

            if str(i['type']) == 'SOA':
                continue

            for j in i.keys():
                if j not in recordTypes[i['type']] and str(j) != 'id':
                    del i[j]

            clean_func = "clean_" + str(i['type'])
            f = getattr(self, clean_func)
            if not f:
                raise ValueError("No validation can be done for key %s" % i['type'])

            if 'id' in i:
                required_fields = ['type', 'id']
            else:
                required_fields = recordTypes[i['type']]

            for j in required_fields:
                if j not in i:
                    raise ValueError('Missing required field (%s) in record.' % str(j))

            tmp = f(i)
            self.cleaned.append(tmp)

    def cleaned_data(self):
        return self.cleaned

    def check_int(self, val):
        try:
            return int(val)
        except:
            raise ValueError("Value must be integer")

    def validate_hostname(self, data):
        r = re.compile('^([a-zA-Z0-9_.-]{,63}\.){1,}[a-zA-Z0-9_.-]{,63}$|^([a-zA-Z0-9_.-]){,63}$|^@$|^[*]$')
        if not r.match(data):
            raise ValueError("Invalid hostname")
        return data

    def validate_mx_data(self, data):
        valid_ip = False
        try:
            val = ip.IPv4Address(data)
            valid_ip = True
        except:
            pass
        try:
            val = ip.IPv6Address(data)
            valid_ip = True
        except:
            pass

        if valid_ip is True:
            raise ValueError("MX entry can not be an IP.")
        r = re.compile('^([a-zA-Z0-9_.-]{,63}\.){1,}[a-zA-Z0-9_.-]{,63}$|^([a-zA-Z0-9_.-]){,63}$|^@$|^[*]$')
        if not r.match(data):
            raise ValueError("Invalid hostname")
        return data

    def validate_ipv4(self, data):
        try:
            ip.IPv4Address(data)
        except Exception:
            raise ValueError('Invalid IPv4 address')
        return data

    def validate_ipv6(self, data):
        try:
            ip.IPv6Address(data)
        except:
            raise ValueError('Invalid IPv4 address')
        return data

    def validate_ttl(self, data):
        try:
            int(data)
        except:
            raise ValueError("Invalid TTL field")
        if int(data) < 600:
            data = 600
        return data

    def validate_type(self, data):
        return data

    def validate_ptr_host(self, data):
        try:
            a = int(data)
            if a > 255 or a < 0:
                raise Exception()
        except:
            raise ValueError('Invalid PTR record')
        return data

    def validate_id(self, data):
        return data

    def validate_srv_data(self, data):
        flds = data.split()
        if len(flds) != 4:
            raise ValueError('Invalid data for SRV record')
        for i in flds[:3]:
            try:
                int(i)
            except:
                raise ValueError("Priority, weight and port must be integers")
        self.validate_hostname(flds[3])
        return data

    def clean_A(self, data):
        flds = {"host": self.validate_hostname, "data": self.validate_ipv4}
        flds.update(self.fields)
        for i in data.keys():
            if i not in flds:
                raise ValueError("No validation can be done for %s" % str(i))
            data[i] = flds[i](data[i])
        return data

    def clean_AAAA(self, data):
        flds = {"host": self.validate_hostname, "data": self.validate_ipv6}
        flds.update(self.fields)
        for i in data.keys():
            if i not in flds:
                raise ValueError("No validation can be done for %s" % str(i))
            data[i] = flds[i](data[i])
        return data

    def clean_MX(self, data):
        flds = {"host": self.validate_hostname, "data": self.validate_mx_data, "priority": self.check_int}
        flds.update(self.fields)
        for i in data.keys():
            if i not in flds:
                raise ValueError("No validation can be done for %s" % str(i))
            data[i] = flds[i](data[i])
        return data

    def clean_NS(self, data):
        flds = {"host": self.validate_hostname, "data": self.validate_hostname}
        flds.update(self.fields)
        for i in data.keys():
            if i not in flds:
                raise ValueError("No validation can be done for %s" % str(i))
            data[i] = flds[i](data[i])
        return data

    def clean_CNAME(self, data):
        flds = {"host": self.validate_hostname, "data": self.validate_hostname}
        flds.update(self.fields)
        for i in data.keys():
            if i not in flds:
                raise ValueError("No validation can be done for %s" % str(i))
            data[i] = flds[i](data[i])
        return data

    def clean_TXT(self, data):
        flds = {"host": self.validate_hostname, "data": func.addQuotes}
        flds.update(self.fields)
        for i in data.keys():
            if i not in flds:
                raise ValueError("No validation can be done for %s" % str(i))
            data[i] = flds[i](data[i])
        return data

    def clean_PTR(self, data):
        flds = {"host": self.validate_hostname, "data": self.validate_hostname}
        flds.update(self.fields)
        for i in data.keys():
            if i not in flds:
                raise ValueError("No validation can be done for %s" % str(i))
            data[i] = flds[i](data[i])
        return data

    def clean_SRV(self, data):
        flds = {"host": self.validate_hostname, "data": self.validate_srv_data}
        flds.update(self.fields)
        for i in data.keys():
            if i not in flds:
                raise ValueError("No validation can be done for %s" % str(i))
            data[i] = flds[i](data[i])
        return data
