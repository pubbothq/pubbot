import time

from constance import config
import gevent
from github3 import GitHub, GitHubError

from pubbot import service
from pubbot.github import signals


class OrganizationEventsService(service.TaskService):

    handlers = {
        'CommitCommentEvent': signals.commit_comment,
        'CreateEvent': signals.create,
        'DeleteEvent': signals.delete,
        'GollumEvent': signals.gollum,
        'IssueCommentEvent': signals.issue_comment,
        'IssuesEvent': signals.issues,
        'MemberEvent': signals.member,
        'PublicEvent': signals.public,
        'PullRequestEvent': signals.pull_request,
        'PullRequestReviewCommentEvent': signals.pull_request_review_comment,
        'PushEvent': signals.push,
        'ReleaseEvent': signals.release,
        'StatusEvent': signals.status,
        'TeamAddEvent': signals.team_add,
        'WatchEvent': signals.watch,
    }

    def is_rate_limited(self, response):
        return int(response.headers.get("X-RateLimit-Remaining", 0)) <= 0

    def seconds_till_ratelimit_reset(self, response):
        ttr = int(response.headers.get("X-RateLimit-Reset", 0)) - time.time()
        return max(ttr, 0)

    def iter_events(self, iter):
        """
        This is an awkward construction to avoid iterating over an event stream that is a 304 :/
        """
        first_event = next(iter)
        if iter.last_response.status_code == 304:
            return
        yield first_event
        while True:
            yield next(iter)

    def iter_new_events(self, iterable, include_recent=False):
        most_recent = None

        while True:
            events = []

            try:
                # Buffer the events in order. We can't yield immediately otherwise
                # the stream will be yielded out of order - which would suck.
                # We buffer until we see an ID we recognise. This avoids dupes.
                for event in self.iter_events(iterable):
                    if event.id == most_recent:
                        self.logger.debug("Event %s already seen. No need to fetch rest of stream" % event.id)
                        break
                    events.append(event)

            except GitHubError as e:
                if e.response.status_code == 403 and self.is_rate_limited(e.response):
                    sleep_time = self.seconds_till_ratelimit_reset(e.response)
                    if sleep_time > 0:
                        self.logger.debug("Sleeping for %d seconds (rate limit hit)" % (sleep_time, ))
                        gevent.sleep(sleep_time)
                        continue
                raise

            if events:
                # For some cases you dont want to yield the entire history.
                # So only bother to yield if user has requested recent history *or*
                # we have looped through the data at least once.
                if include_recent or most_recent:
                    while events:
                        last_event = events.pop()
                        yield last_event
                most_recent = last_event.id

            poll_interval = int(iterable.last_response.headers.get("X-Poll-Interval", 0))
            if poll_interval > 0:
                self.logger.debug("Sleeping for %d seconds (due to X-Poll-Interval)" % (poll_interval, ))
                gevent.sleep(poll_interval)

            iterable.refresh()

    def run(self):
        org = self.parent.gh.organization(self.name)
        for event in self.iter_new_events(org.iter_events()):
            signal = self.handlers.get(event.type)
            if not signal:
                self.logger.info("Unhandled event: %s" % event.to_json())
            signal.send(payload=event.payload)


class Service(service.BaseService):

    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)

        if config.GITHUB_TOKEN:
            self.gh = GitHub(token=config.GITHUB_TOKEN)
        else:
            self.gh = GitHub()

        if config.GITHUB_FOLLOW_ORGS:
            for org in config.GITHUB_FOLLOW_ORGS.split(","):
                self.add_child(OrganizationEventsService(org))
