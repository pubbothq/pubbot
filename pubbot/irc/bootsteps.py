from celery import bootsteps
from geventirc.irc import Client
from geventirc import handlers, replycode

from pubbot.irc.models import Network
from pubbot.irc.handlers import *


# FIXME: It would be nice if this global didn't exist..
clients = {}

class IrcStep(bootsteps.StartStopStep):

    running = False

    def start(self, worker):
        if not 'irc' in worker.app.amqp.queues:
            return
        self.running = True

        print "Starting irc services"
        self.group = []
        for network in Network.objects.all():
            print "Connecting to '%s' on port '%d'" % (network.server, int(network.port))

            client = Client(network.server, 'pubbot2', port=str(network.port))
            clients[network.server] = client

            # House keeping handlers
            client.add_handler(handlers.ping_handler, 'PING')
            client.add_handler(handlers.nick_in_use_handler, replycode.ERR_NICKNAMEINUSE)
            client.add_handler(UserListHandler())
            client.add_handler(InviteProcessor())

            # Channels to join
            for room in network.rooms.all():
                client.add_handler(handlers.JoinHandler(room.room, False))

            # Inject conversation data into queue
            client.add_handler(ConversationHandler())

            client.start()

            self.group.append(client)

    def stop(self, worker):
        if self.running:
            print "Stopping irc services"
            [c.stop() for c in self.group]

