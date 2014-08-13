
import os
import sys

from progressbar import ProgressBar

from django.core.management.base import BaseCommand, CommandError

from pubbot.chat.reading import learn_string


class Command(BaseCommand):
    args = '<path>'
    help = 'Import the specified irc log into the chat brain'

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("Path to log file not specified")
        elif len(args) > 1:
            raise CommandError("Can only import one log file at a time")

        path = args[0]
        if not os.path.exists(path):
            raise CommandError("No irc log found at %r" % path)

        pb = ProgressBar(maxval=os.stat(path).st_size).start()

        ignored_nicks = options.get("ignored_nick", [])

        with open(path) as fp:
            for line in fp.readlines():
                # Couple of problems with this approach.
                #  1. len() doesn't give size in bytes
                #  2. Ideally we'd set the size *after* each iteration
                pb.update(len(line))
                sys.stdout.flush()

                if line.startswith("---"):
                    continue

                if line[2] != ":":
                    continue

                line = line[6:]

                # If this line doesn't start with < then there isn't a nick, so
                # there isnt a chat line.
                if not line.startswith("<"):
                    continue

                nick, line = line.split(">", 1)

                # Is this nick blacklisted? (Best to ignore chatbot spam)
                if nick.lower() in ignored_nicks:
                    continue

                # Does this line actually have sentences?
                if " " not in line:
                    continue

                learn_string(line)

        pb.finish()

        self.stdout.write('I readed the log file')
