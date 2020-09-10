import logging

from cryptoxlib.version_conversions import get_current_time_ms

LOG = logging.getLogger(__name__)


class Timer(object):
    def __init__(self, name: str, active: bool = True) -> None:
        self.name = name
        self.active = active

        self.start_tmstmp_ms = None

    def __enter__(self) -> None:
        if self.active:
            self.start_tmstmp_ms = get_current_time_ms()

    def __exit__(self, type, value, traceback) -> None:
        if self.active:
            LOG.debug(f'Timer {self.name} finished. Took {round((get_current_time_ms() - self.start_tmstmp_ms), 3)} ms.')