class bindRouter(object):

    def db_for_read(self, model, **hints):
        "Point all operations on dns models to 'bind'"
        if model._meta.db_table == 'dns_records':
            return 'bind'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.db_table == 'dns_records':
            return 'bind'
        return None

#    def allow_syncdb(self, db, model):
#        if db == 'bind' and model._meta.db_table == 'dns_records':
#            return True
#        elif db == 'default' and model._meta.db_table != 'dns_records':
#            return True
#        return False
