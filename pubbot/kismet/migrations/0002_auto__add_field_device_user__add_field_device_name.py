# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Device.user'
        db.add_column(u'kismet_device', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(
                          blank=True, related_name='devices', null=True, to=orm['main.UserProfile']),
                      keep_default=False)

        # Adding field 'Device.name'
        db.add_column(u'kismet_device', 'name',
                      self.gf('django.db.models.fields.CharField')(
                          max_length=64, null=True, blank=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Device.user'
        db.delete_column(u'kismet_device', 'user_id')

        # Deleting field 'Device.name'
        db.delete_column(u'kismet_device', 'name')

    models = {
        u'kismet.device': {
            'Meta': {'object_name': 'Device'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '17'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'opt_out': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'devices'", 'null': 'True', 'to': u"orm['main.UserProfile']"})
        },
        u'kismet.network': {
            'Meta': {'ordering': "['name']", 'object_name': 'Network'},
            'bssid': ('django.db.models.fields.CharField', [], {'max_length': '17'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'kismet.times': {
            'Meta': {'object_name': 'Times'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'times'", 'to': u"orm['kismet.Device']"}),
            'first_seen': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'main.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['kismet']
