import logging
import datetime

LOG = logging.getLogger(__name__)


class PeriodicChecker(object):
    def __init__(self, period_ms):
        self.period_ms = period_ms
        self.last_exec_tmstmp_ms = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp() * 1000)

    def check(self) -> bool:
        now_tmstmp_ms = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp() * 1000)
        if self.last_exec_tmstmp_ms + self.period_ms < now_tmstmp_ms:
            self.last_exec_tmstmp_ms = now_tmstmp_ms
            return True
        else:
            return False