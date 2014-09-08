from croniter import croniter

from pubbot.service import TaskService


class ScheduledTask(object):

    def __init__(self, schedule, task):
        self.schedule = schedule
        self.task = task
        self.croniter = croniter(self)
        self.refresh()

    def refresh(self):
        self.due = self.croniter.get_next()

    def maybe_apply(self):
        if self.due < time.time():
            gevent.spawn(self.task)
            self.refresh()
            return True


class Service(TaskService):

    """
    A service that maintains a list of cron type schedules, calling their
    associated tasks at the right time.
    """

    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        self.tasks = []

        # FIXME: Do some discovery here to populate self.tasks wth
        # ScheduledTask objects.

    def run(self):
        while self.tasks:
            for task in self.tasks:
                if not task.maybe_apply():
                    break

            self.tasks.sort(key=lambda task: task.due)

            next_due = self.tasks[0].due
            self.logger.info("A beat is next due at %r" % next_due)

            ttb = next_due - time.time()
            self.logger.debug("Time-to-beat is %r" % ttb)

            gevent.sleep(max(ttb, 0))
