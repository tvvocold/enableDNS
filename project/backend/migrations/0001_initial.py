# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'userProfile'
        db.create_table(u'auth_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('maxDoms', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('global_records_per_zone', self.gf('django.db.models.fields.IntegerField')(default=1000)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=192, blank=True)),
            ('alternate_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('prefered_language', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('public_profile_field', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_api', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'backend', ['userProfile'])

        # Adding model 'DnsRecords'
        db.create_table(u'dns_records', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zone', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=192, blank=True)),
            ('host', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=192, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='3600', max_length=24, db_index=True, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ttl', self.gf('django.db.models.fields.IntegerField')(default=3600)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('refresh', self.gf('django.db.models.fields.IntegerField')(default=3600)),
            ('retry', self.gf('django.db.models.fields.IntegerField')(default=3600)),
            ('expire', self.gf('django.db.models.fields.IntegerField')(default=86400)),
            ('minimum', self.gf('django.db.models.fields.IntegerField')(default=3600)),
            ('serial', self.gf('django.db.models.fields.IntegerField')(default=2008082700)),
            ('resp_person', self.gf('django.db.models.fields.CharField')(default='resp.person.email', max_length=192)),
            ('primary_ns', self.gf('django.db.models.fields.CharField')(default='ns1.yourdns.here', max_length=192)),
            ('data_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'backend', ['DnsRecords'])

        # Adding model 'suffixes'
        db.create_table(u'backend_suffixes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'backend', ['suffixes'])

        # Adding model 'dnsZones'
        db.create_table(u'Zones', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zone_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=192)),
            ('add_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'backend', ['dnsZones'])

        # Adding model 'zoneMeta'
        db.create_table(u'dns_zonemeta', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zone_name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['backend.dnsZones'])),
            ('max_records', self.gf('django.db.models.fields.IntegerField')(default=1000)),
        ))
        db.send_create_signal(u'backend', ['zoneMeta'])

        # Adding model 'ServiceTemplates'
        db.create_table(u'services_servicetemplates', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=192)),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'backend', ['ServiceTemplates'])

        # Adding model 'ZoneServices'
        db.create_table(u'services_zoneservices', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zone_name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['backend.dnsZones'])),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['backend.ServiceTemplates'])),
            ('record_ids', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'backend', ['ZoneServices'])

        # Adding unique constraint on 'ZoneServices', fields ['zone_name', 'template']
        db.create_unique(u'services_zoneservices', ['zone_name_id', 'template_id'])

        # Adding model 'ZoneShares'
        db.create_table(u'backend_zoneshares', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['backend.dnsZones'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'backend', ['ZoneShares'])

        # Adding unique constraint on 'ZoneShares', fields ['zone', 'user']
        db.create_unique(u'backend_zoneshares', ['zone_id', 'user_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ZoneShares', fields ['zone', 'user']
        db.delete_unique(u'backend_zoneshares', ['zone_id', 'user_id'])

        # Removing unique constraint on 'ZoneServices', fields ['zone_name', 'template']
        db.delete_unique(u'services_zoneservices', ['zone_name_id', 'template_id'])

        # Deleting model 'userProfile'
        db.delete_table(u'auth_userprofile')

        # Deleting model 'DnsRecords'
        db.delete_table(u'dns_records')

        # Deleting model 'suffixes'
        db.delete_table(u'backend_suffixes')

        # Deleting model 'dnsZones'
        db.delete_table(u'Zones')

        # Deleting model 'zoneMeta'
        db.delete_table(u'dns_zonemeta')

        # Deleting model 'ServiceTemplates'
        db.delete_table(u'services_servicetemplates')

        # Deleting model 'ZoneServices'
        db.delete_table(u'services_zoneservices')

        # Deleting model 'ZoneShares'
        db.delete_table(u'backend_zoneshares')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'backend.dnsrecords': {
            'Meta': {'object_name': 'DnsRecords', 'db_table': "u'dns_records'"},
            'data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'data_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'expire': ('django.db.models.fields.IntegerField', [], {'default': '86400'}),
            'host': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '192', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minimum': ('django.db.models.fields.IntegerField', [], {'default': '3600'}),
            'primary_ns': ('django.db.models.fields.CharField', [], {'default': "'ns1.yourdns.here'", 'max_length': '192'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'refresh': ('django.db.models.fields.IntegerField', [], {'default': '3600'}),
            'resp_person': ('django.db.models.fields.CharField', [], {'default': "'resp.person.email'", 'max_length': '192'}),
            'retry': ('django.db.models.fields.IntegerField', [], {'default': '3600'}),
            'serial': ('django.db.models.fields.IntegerField', [], {'default': '2008082700'}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'default': '3600'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'3600'", 'max_length': '24', 'db_index': 'True', 'blank': 'True'}),
            'zone': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '192', 'blank': 'True'})
        },
        u'backend.dnszones': {
            'Meta': {'object_name': 'dnsZones', 'db_table': "u'Zones'"},
            'add_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'zone_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '192'})
        },
        u'backend.servicetemplates': {
            'Meta': {'object_name': 'ServiceTemplates', 'db_table': "u'services_servicetemplates'"},
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '192'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
        },
        u'backend.suffixes': {
            'Meta': {'object_name': 'suffixes'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'backend.userprofile': {
            'Meta': {'object_name': 'userProfile', 'db_table': "u'auth_userprofile'"},
            'alternate_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'global_records_per_zone': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'has_api': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'maxDoms': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '192', 'blank': 'True'}),
            'prefered_language': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'public_profile_field': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'backend.zonemeta': {
            'Meta': {'object_name': 'zoneMeta', 'db_table': "u'dns_zonemeta'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_records': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'zone_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['backend.dnsZones']"})
        },
        u'backend.zoneservices': {
            'Meta': {'unique_together': "(('zone_name', 'template'),)", 'object_name': 'ZoneServices', 'db_table': "u'services_zoneservices'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'record_ids': ('django.db.models.fields.TextField', [], {}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['backend.ServiceTemplates']"}),
            'zone_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['backend.dnsZones']"})
        },
        u'backend.zoneshares': {
            'Meta': {'unique_together': "(('zone', 'user'),)", 'object_name': 'ZoneShares'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['backend.dnsZones']"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['backend']