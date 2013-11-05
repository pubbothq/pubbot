# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Network'
        db.create_table(u'kismet_network', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bssid', self.gf('django.db.models.fields.CharField')(max_length=17)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'kismet', ['Network'])

        # Adding model 'Device'
        db.create_table(u'kismet_device', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mac', self.gf('django.db.models.fields.CharField')(max_length=17)),
            ('opt_out', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'kismet', ['Device'])

        # Adding model 'Times'
        db.create_table(u'kismet_times', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(related_name='times', to=orm['kismet.Device'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('first_seen', self.gf('django.db.models.fields.DateTimeField')()),
            ('last_seen', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'kismet', ['Times'])


    def backwards(self, orm):
        # Deleting model 'Network'
        db.delete_table(u'kismet_network')

        # Deleting model 'Device'
        db.delete_table(u'kismet_device')

        # Deleting model 'Times'
        db.delete_table(u'kismet_times')


    models = {
        u'kismet.device': {
            'Meta': {'object_name': 'Device'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '17'}),
            'opt_out': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
        }
    }

    complete_apps = ['kismet']