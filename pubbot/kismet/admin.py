
from django.contrib import admin
from pubbot.irc.models import Network, Channel


class ChannelInline(admin.TabularInline):
    model = Channel


class NetworkAdmin(admin.ModelAdmin):
    inlines = [
        ChannelInline,
        ]


admin.site.register(Network, NetworkAdmin)
admin.site.register(Channel)

