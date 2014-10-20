
import os
import sys
from optparse import make_option

from progressbar import ProgressBar, Percentage, Bar, ETA

from django.core.management.base import BaseCommand, CommandError

from pubbot.chat.brain import brain


class Command(BaseCommand):
    args = '<path>'
    help = 'Import the specified irc log into the chat brain'

    option_list = BaseCommand.option_list + (
        make_option(
            '--ignored_nicks',
            action='append',
            dest='ignored_nicks',
            default=[],
            help="Don't import message by this nick"
        ),
        make_option(
            '--start-at',
            action='store',
            dest='start_at',
            default=1,
            help="Start at line <x>",
        ),
    )

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("Path to log file not specified")
        elif len(args) > 1:
            raise CommandError("Can only import one log file at a time")

        path = args[0]
        if not os.path.exists(path):
            raise CommandError("No irc log found at %r" % path)

        ignored_nicks = options.get("ignored_nick", [])

        brain.client.flushdb()

        with open(path) as fp:
                start_at = int(options.get('start_at', 0))
                lines = fp.readlines()[start_at:]

                pb = ProgressBar(widgets=[Percentage(), Bar(), ETA()], maxval=len(lines)).start()

                for line in lines:
                    pb.update(pb.currval + 1)
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

                    nick, line = line[1:].split(">", 1)

                    nick = nick.strip().lstrip("@")
                    line = line.strip()

                    # Try to find directed messages. Grr.
                    # So treat: pubbot: hello boy
                    # As: hello boy
                    if ":" in line:
                        l, r = line.split(":", 1)
                        if " " not in l:
                            continue

                    # Is this nick blacklisted? (Best to ignore chatbot spam)
                    if nick.lower() in ignored_nicks:
                        continue

                    # Does this line actually have sentences?
                    if " " not in line:
                        continue

                    brain.store_string(line)

        pb.finish()

        self.stdout.write('I readed the log file')
