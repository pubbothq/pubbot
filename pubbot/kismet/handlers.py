
import datetime
import time
import pytz

from pubbot.main.utils import broadcast
from pubbot.kismet.models import Network, Device, Times


class ClientFinder(object):

    handles = ['CLIENT']

    def __call__(self, packet_type, packet):
        bssid, mac, typ, lasttime, datapackets = packet

        if lasttime == 0:
            return

        now = datetime.datetime.now()
        dt = datetime.datetime(*time.localtime(int(lasttime))[0:6])

        if (now - dt) > datetime.timedelta(0, 60, 0):
            # Too old...
            return

        if not Network.objects.filter(bssid=bssid, enabled=True).exists():
            return

        device, _ = Device.objects.get_or_create(mac=mac)

        if device.opt_out:
            return

        try:
            t = device.times.get(date=datetime.date.today())
            t.last_seen = pytz.utc.localize(dt)
            t.save()

        except Times.DoesNotExist:
            Times(device=device, date=dt, first_seen=dt, last_seen=dt).save()
            broadcast(
                kind="device.arrived",
                mac=mac,
                arrived=dt,
                device_id=device.id,
            )


class NetworkFinder(object):

    handles = ['NETWORK']

    def __call__(self, packet_type, packet):
        bssid, typ, ssid, channel, lasttime = packet

        if lasttime == 0:
            return

        if ssid == "<no ssid>":
            return

        now = datetime.datetime.now()
        dt = datetime.datetime(*time.localtime(int(lasttime))[0:6])

        if (now - dt) > datetime.timedelta(0, 60, 0):
            # Too old...
            return

        network, _ = Network.objects.get_or_create(bssid=bssid)
        network.name = ssid
        network.save()
